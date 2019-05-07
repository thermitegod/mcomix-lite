# -*- coding: utf-8 -*-

"""PDF handler"""

import math
import os
import re
from distutils.version import LooseVersion

from mcomix import log, process
from mcomix.archive import archive_base

# Default DPI for rendering.
PDF_RENDER_DPI_DEF = 72 * 4
# Maximum DPI for rendering.
PDF_RENDER_DPI_MAX = 72 * 10

_pdf_possible = None
_mutool_exec = None
_mudraw_exec = None
_mudraw_trace_args = None


class PdfArchive(archive_base.BaseArchive):
    """Concurrent calls to extract welcome"""
    support_concurrent_extractions = True

    _fill_image_regex = re.compile(r'^\s*<fill_image\b.*\bmatrix="(?P<matrix>[^"]+)".*\bwidth="(?P<width>\d+)".*\bheight="(?P<height>\d+)".*/>\s*$')

    def __init__(self, archive):
        super(PdfArchive, self).__init__(archive)

    def iter_contents(self):
        with process.popen(_mutool_exec + ['show', '--', self.archive, 'pages'],
                           universal_newlines=True) as proc:
            for line in proc.stdout:
                if line.startswith('page '):
                    yield line.split()[1] + '.png'

    def extract(self, filename, destination_dir):
        self._create_directory(destination_dir)
        destination_path = os.path.join(destination_dir, filename)
        page_num = int(filename[0:-4])
        # Try to find optimal DPI.
        cmd = _mudraw_exec + _mudraw_trace_args + ['--', self.archive, str(page_num)]
        log.debug('finding optimal DPI for %s: %s', filename, ' '.join(cmd))
        with process.popen(cmd, universal_newlines=True) as proc:
            max_size = 0
            max_dpi = PDF_RENDER_DPI_DEF
            for line in proc.stdout:
                match = self._fill_image_regex.match(line)
                if not match:
                    continue
                matrix = [float(f) for f in match.group('matrix').split()]
                for size, coeff1, coeff2 in (
                        (int(match.group('width')), matrix[0], matrix[1]),
                        (int(match.group('height')), matrix[2], matrix[3]),
                ):
                    if size < max_size:
                        continue
                    render_size = math.sqrt(coeff1 * coeff1 + coeff2 * coeff2)
                    dpi = int(size * 72 / render_size)
                    if dpi > PDF_RENDER_DPI_MAX:
                        dpi = PDF_RENDER_DPI_MAX
                    max_size = size
                    max_dpi = dpi
        # Render...
        cmd = _mudraw_exec + ['-r', str(max_dpi), '-o', destination_path, '--', self.archive, str(page_num)]
        log.debug('rendering %s: %s', filename, ' '.join(cmd))
        process.call(cmd)
        return destination_path

    @staticmethod
    def is_available():
        global _pdf_possible
        if _pdf_possible is not None:
            return _pdf_possible
        global _mutool_exec, _mudraw_exec, _mudraw_trace_args
        mutool = process.find_executable('mutool')
        _pdf_possible = False
        version = None
        if mutool is None:
            log.debug('mutool executable not found')
        else:
            _mutool_exec = [mutool]
            with process.popen([mutool, '-v'],
                               stdout=process.NULL,
                               stderr=process.PIPE,
                               universal_newlines=True) as proc:
                output = proc.stderr.read()
                if output.startswith('mutool version '):
                    version = output[15:].rstrip()
            version = LooseVersion(version)
            _mudraw_exec = [mutool, 'draw']
            _mudraw_trace_args = ['-F', 'trace']
            _pdf_possible = True

        if _pdf_possible:
            log.info('Using MuPDF version: %s', version)
            log.debug('mutool: %s', ' '.join(_mutool_exec))
            log.debug('mudraw: %s', ' '.join(_mudraw_exec))
            log.debug('mudraw trace arguments: %s', ' '.join(_mudraw_trace_args))
        else:
            log.info('MuPDF not available.')
        return _pdf_possible

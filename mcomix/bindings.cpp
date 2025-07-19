/**
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include "enums.hpp"
#include "file_provider.hpp"
#include "supported.hpp"
#include "package.hpp"
#include "sort/sort.hpp"

#include "gui/lib/box.hpp"
#include "gui/lib/layout.hpp"
#include "gui/lib/zoom.hpp"

#include <nanobind/nanobind.h>
#include <nanobind/stl/array.h>
#include <nanobind/stl/filesystem.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>

namespace nb = nanobind;
using namespace nb::literals;

NB_MODULE(mcomix_compiled, m)
{
    nb::set_leak_warnings(false);

    nb::enum_<Animation>(m, "Animation")
        .def("__int__", [](Animation v) { return static_cast<std::int32_t>(v); })
        .value("DISABLED", Animation::DISABLED)
        .value("NORMAL", Animation::NORMAL);

    nb::enum_<ConfigType>(m, "ConfigType")
        .value("CONFIG", ConfigType::CONFIG)
        .value("KEYBINDINGS", ConfigType::KEYBINDINGS);

    nb::enum_<DoublePage>(m, "DoublePage")
        .def("__int__", [](DoublePage v) { return static_cast<std::int32_t>(v); })
        .value("NEVER", DoublePage::NEVER)
        .value("AS_ONE_TITLE", DoublePage::AS_ONE_TITLE)
        .value("AS_ONE_WIDE", DoublePage::AS_ONE_WIDE)
        .value("ALWAYS", DoublePage::ALWAYS);

    nb::enum_<FileSortType>(m, "FileSortType")
        .def("__int__", [](FileSortType v) { return static_cast<std::int32_t>(v); })
        .value("NONE", FileSortType::NONE)
        .value("NAME", FileSortType::NAME)
        .value("SIZE", FileSortType::SIZE)
        .value("LAST_MODIFIED", FileSortType::LAST_MODIFIED)
        .value("NAME_LITERAL", FileSortType::NAME_LITERAL);

    nb::enum_<FileSortDirection>(m, "FileSortDirection")
        .def("__int__", [](FileSortDirection v) { return static_cast<std::int32_t>(v); })
        .value("DESCENDING", FileSortDirection::DESCENDING)
        .value("ASCENDING", FileSortDirection::ASCENDING);

    nb::enum_<FileTypes>(m, "FileTypes")
        .def("__int__", [](FileTypes v) { return static_cast<std::int32_t>(v); })
        .value("IMAGES", FileTypes::IMAGES)
        .value("ARCHIVES", FileTypes::ARCHIVES);

    nb::enum_<Scroll>(m, "Scroll")
        .def("__int__", [](Scroll v) { return static_cast<std::int32_t>(v); })
        .value("END", Scroll::END)
        .value("START", Scroll::START)
        .value("CENTER", Scroll::CENTER);

    nb::enum_<ZoomModes>(m, "ZoomModes")
        .def("__int__", [](ZoomModes v) { return static_cast<std::int32_t>(v); })
        .value("BEST", ZoomModes::BEST)
        .value("WIDTH", ZoomModes::WIDTH)
        .value("HEIGHT", ZoomModes::HEIGHT)
        .value("MANUAL", ZoomModes::MANUAL)
        .value("SIZE", ZoomModes::SIZE);

    nb::enum_<ZoomAxis>(m, "ZoomAxis")
        .def("__int__", [](ZoomAxis v) { return static_cast<std::int32_t>(v); })
        .value("DISTRIBUTION", ZoomAxis::DISTRIBUTION)
        .value("ALIGNMENT", ZoomAxis::ALIGNMENT)
        .value("WIDTH", ZoomAxis::WIDTH)
        .value("HEIGHT", ZoomAxis::HEIGHT);

    nb::class_<PackageInfo>(m, "PackageInfo")
        .def_prop_ro_static("APP_NAME", [](nb::handle) { return PackageInfo::APP_NAME; })
        .def_prop_ro_static("PROG_NAME", [](nb::handle) { return PackageInfo::PROG_NAME; })
        .def_prop_ro_static("VERSION", [](nb::handle) { return PackageInfo::VERSION; });

    nb::class_<Box>(m, "Box")
        .def(nb::init<>())
        .def(nb::init<const std::vector<std::int32_t>&, const std::vector<std::int32_t>&>(),
             "position"_a,
             "size"_a = std::vector<std::int32_t>{})
        .def("dimensions", &Box::dimensions)
        .def("get_size", &Box::get_size)
        .def("get_position", &Box::get_position)
        .def("set_position", &Box::set_position)
        .def("translate_opposite", &Box::translate_opposite)
        .def_static("box_to_center_offset_1d", &Box::box_to_center_offset_1d)
        .def_static("align_center", &Box::align_center)
        .def_static("distribute", &Box::distribute, "boxes"_a, "axis"_a, "fit"_a, "spacing"_a = 2)
        .def("wrapper_box", &Box::wrapper_box)
        .def_static("bounding_box", &Box::bounding_box)
        .def("__eq__", [](const Box& a, const Box& b) { return a == b; });

    nb::class_<file_provider>(m, "FileProvider")
        .def(nb::init<>())
        .def(nb::init<const std::vector<std::filesystem::path>&>())
        .def("list_files", &file_provider::list_files);

    nb::class_<Layout>(m, "Layout")
        .def(nb::init<const std::vector<std::array<std::int32_t, 2>>&,
                      const std::array<std::int32_t, 2>&,
                      const std::array<std::int32_t, 2>&,
                      ZoomAxis,
                      ZoomAxis>(),
             "content_sizes"_a,
             "viewport_size"_a,
             "orientation"_a,
             "distribution_axis"_a,
             "alignment_axis"_a)
        .def("scroll_to_predefined", &Layout::scroll_to_predefined, "destination"_a)
        .def("get_content_boxes", &Layout::get_content_boxes)
        .def("get_union_box", &Layout::get_union_box)
        .def("get_viewport_box", &Layout::get_viewport_box)
        .def("get_orientation", &Layout::get_orientation)
        .def("set_orientation", &Layout::set_orientation, "new_orientation"_a);

    nb::class_<ZoomModel>(m, "ZoomModel")
        .def(nb::init<>())
        .def("set_fit_mode", &ZoomModel::set_fit_mode, "fitmode"_a)
        .def("set_scale_up", &ZoomModel::set_scale_up, "scale_up"_a)
        .def("set_user_zoom_log", &ZoomModel::set_user_zoom_log, "zoom_log"_a)
        .def("zoom_in", &ZoomModel::zoom_in)
        .def("zoom_out", &ZoomModel::zoom_out)
        .def("reset_user_zoom", &ZoomModel::reset_user_zoom)
        .def("scale", &ZoomModel::scale, "t"_a, "factor"_a)
        .def("get_zoomed_size",
             &ZoomModel::get_zoomed_size,
             "image_sizes"_a,
             "screen_size"_a,
             "distribution_axis"_a,
             "do_not_transform"_a)
        .def("preferred_scale", &ZoomModel::preferred_scale, "image_size"_a, "limits"_a, "distribution_axis"_a)
        .def("calc_limits", &ZoomModel::calc_limits, "union_size"_a, "screen_size"_a, "fitmode"_a, "allow_upscaling"_a)
        .def("scale_distributed",
             &ZoomModel::scale_distributed,
             "sizes"_a,
             "axis"_a,
             "max_size"_a,
             "allow_upscaling"_a,
             "do_not_transform"_a)
        .def("scale_image_size", &ZoomModel::scale_image_size, "size"_a, "scale"_a)
        .def("round_nonempty", &ZoomModel::round_nonempty, "t"_a)
        .def("fix_page_sizes", &ZoomModel::fix_page_sizes, "image_sizes"_a, "distribution_axis"_a, "do_not_transform"_a)
        .def("union_size", &ZoomModel::union_size, "image_sizes"_a, "distribution_axis"_a);

    m.def("sort_alphanumeric", &sort_alphanumeric);
    m.def("is_archive", &is_archive);
    m.def("is_image", &is_image);

    m.def("supported_archive_extensions",
          []()
          {
              static const auto exts = supported_archive_extensions();
              return std::vector<std::string>(exts.begin(), exts.end());
          });

    m.def("supported_image_extensions",
          []()
          {
              static const auto exts = supported_image_extensions();
              return std::vector<std::string>(exts.begin(), exts.end());
          });
}

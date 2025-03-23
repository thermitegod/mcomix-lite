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

#include "box.hpp"
#include "layout.hpp"
#include "zoom.hpp"
#include "sort/sort.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>

namespace pybind11::detail
{
template<> struct type_caster<ZoomModes>
{
  public:
    PYBIND11_TYPE_CASTER(ZoomModes, _("ZoomModes"));

    bool
    load(handle src, bool)
    {
        if (!src || !PyLong_Check(src.ptr()))
        {
            return false;
        }
        value = static_cast<ZoomModes>(PyLong_AsLong(src.ptr()));
        return true;
    }

    static handle
    cast(ZoomModes src, return_value_policy, handle)
    {
        return PyLong_FromLong(static_cast<long>(src));
    }
};
} // namespace pybind11::detail

namespace py = pybind11;

PYBIND11_MODULE(mcomix_compiled, m)
{
    py::class_<Box>(m, "Box")
        .def(py::init<>())
        .def(py::init<const std::vector<std::int32_t>&, const std::vector<std::int32_t>&>(),
             py::arg("position"),
             py::arg("size") = std::vector<std::int32_t>{})
        .def("dimensions", &Box::dimensions)
        .def("get_size", &Box::get_size)
        .def("get_position", &Box::get_position)
        .def("set_position", &Box::set_position)
        .def("translate_opposite", &Box::translate_opposite)
        .def_static("box_to_center_offset_1d", &Box::box_to_center_offset_1d)
        .def_static("align_center", &Box::align_center)
        .def_static("distribute",
                    &Box::distribute,
                    py::arg("boxes"),
                    py::arg("axis"),
                    py::arg("fit"),
                    py::arg("spacing") = 2)
        .def("wrapper_box", &Box::wrapper_box)
        .def_static("bounding_box", &Box::bounding_box)
        .def(py::self == py::self);

    py::class_<Layout>(m, "Layout")
        .def(py::init<const std::vector<std::array<std::int32_t, 2>>&,
                      const std::array<std::int32_t, 2>&,
                      const std::array<std::int32_t, 2>&,
                      std::int32_t,
                      std::int32_t>(),
             py::arg("content_sizes"),
             py::arg("viewport_size"),
             py::arg("orientation"),
             py::arg("distribution_axis"),
             py::arg("alignment_axis"))
        .def("scroll_to_predefined", &Layout::scroll_to_predefined, py::arg("destination"))
        .def("get_content_boxes", &Layout::get_content_boxes)
        .def("get_union_box", &Layout::get_union_box)
        .def("get_viewport_box", &Layout::get_viewport_box)
        .def("get_orientation", &Layout::get_orientation)
        .def("set_orientation", &Layout::set_orientation, py::arg("new_orientation"));

    py::class_<ZoomModel>(m, "ZoomModel")
        .def(py::init<>())
        .def("set_fit_mode", &ZoomModel::set_fit_mode, py::arg("fitmode"))
        .def("set_scale_up", &ZoomModel::set_scale_up, py::arg("scale_up"))
        .def("set_user_zoom_log", &ZoomModel::set_user_zoom_log, py::arg("zoom_log"))
        .def("zoom_in", &ZoomModel::zoom_in)
        .def("zoom_out", &ZoomModel::zoom_out)
        .def("reset_user_zoom", &ZoomModel::reset_user_zoom)
        .def("scale", &ZoomModel::scale, py::arg("t"), py::arg("factor"))
        .def("get_zoomed_size",
             &ZoomModel::get_zoomed_size,
             py::arg("image_sizes"),
             py::arg("screen_size"),
             py::arg("distribution_axis"),
             py::arg("do_not_transform"))
        .def("preferred_scale",
             &ZoomModel::preferred_scale,
             py::arg("image_size"),
             py::arg("limits"),
             py::arg("distribution_axis"))
        .def("calc_limits",
             &ZoomModel::calc_limits,
             py::arg("union_size"),
             py::arg("screen_size"),
             py::arg("fitmode"),
             py::arg("allow_upscaling"))
        .def("scale_distributed",
             &ZoomModel::scale_distributed,
             py::arg("sizes"),
             py::arg("axis"),
             py::arg("max_size"),
             py::arg("allow_upscaling"),
             py::arg("do_not_transform"))
        .def("scale_image_size", &ZoomModel::scale_image_size, py::arg("size"), py::arg("scale"))
        .def("round_nonempty", &ZoomModel::round_nonempty, py::arg("t"))
        .def("fix_page_sizes",
             &ZoomModel::fix_page_sizes,
             py::arg("image_sizes"),
             py::arg("distribution_axis"),
             py::arg("do_not_transform"))
        .def("union_size", &ZoomModel::union_size, py::arg("image_sizes"), py::arg("distribution_axis"));

    m.def("sort_alphanumeric", &sort_alphanumeric, "sort filelist");
}

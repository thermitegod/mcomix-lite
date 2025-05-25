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
#include "supported.hpp"
#include "package.hpp"
#include "sort/sort.hpp"

#include "gui/lib/box.hpp"
#include "gui/lib/layout.hpp"
#include "gui/lib/zoom.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>

namespace pybind11::detail
{
template<> struct type_caster<Animation>
{
  public:
    PYBIND11_TYPE_CASTER(Animation, _("Animation"));

    bool
    load(handle src, bool)
    {
        if (!src || !PyLong_Check(src.ptr()))
        {
            return false;
        }
        value = static_cast<Animation>(PyLong_AsLong(src.ptr()));
        return true;
    }

    static handle
    cast(Animation src, return_value_policy, handle)
    {
        return PyLong_FromLong(static_cast<long>(src));
    }
};

template<> struct type_caster<ConfigType>
{
  public:
    PYBIND11_TYPE_CASTER(ConfigType, _("ConfigType"));

    bool
    load(handle src, bool)
    {
        if (!src || !PyLong_Check(src.ptr()))
        {
            return false;
        }
        value = static_cast<ConfigType>(PyLong_AsLong(src.ptr()));
        return true;
    }

    static handle
    cast(ConfigType src, return_value_policy, handle)
    {
        return PyLong_FromLong(static_cast<long>(src));
    }
};

template<> struct type_caster<DialogChoice>
{
  public:
    PYBIND11_TYPE_CASTER(DialogChoice, _("DialogChoice"));

    bool
    load(handle src, bool)
    {
        if (!src || !PyLong_Check(src.ptr()))
        {
            return false;
        }
        value = static_cast<DialogChoice>(PyLong_AsLong(src.ptr()));
        return true;
    }

    static handle
    cast(DialogChoice src, return_value_policy, handle)
    {
        return PyLong_FromLong(static_cast<long>(src));
    }
};

template<> struct type_caster<DoublePage>
{
  public:
    PYBIND11_TYPE_CASTER(DoublePage, _("DoublePage"));

    bool
    load(handle src, bool)
    {
        if (!src || !PyLong_Check(src.ptr()))
        {
            return false;
        }
        value = static_cast<DoublePage>(PyLong_AsLong(src.ptr()));
        return true;
    }

    static handle
    cast(DoublePage src, return_value_policy, handle)
    {
        return PyLong_FromLong(static_cast<long>(src));
    }
};

template<> struct type_caster<FileSortType>
{
  public:
    PYBIND11_TYPE_CASTER(FileSortType, _("FileSortType"));

    bool
    load(handle src, bool)
    {
        if (!src || !PyLong_Check(src.ptr()))
        {
            return false;
        }
        value = static_cast<FileSortType>(PyLong_AsLong(src.ptr()));
        return true;
    }

    static handle
    cast(FileSortType src, return_value_policy, handle)
    {
        return PyLong_FromLong(static_cast<long>(src));
    }
};

template<> struct type_caster<FileSortDirection>
{
  public:
    PYBIND11_TYPE_CASTER(FileSortDirection, _("FileSortDirection"));

    bool
    load(handle src, bool)
    {
        if (!src || !PyLong_Check(src.ptr()))
        {
            return false;
        }
        value = static_cast<FileSortDirection>(PyLong_AsLong(src.ptr()));
        return true;
    }

    static handle
    cast(FileSortDirection src, return_value_policy, handle)
    {
        return PyLong_FromLong(static_cast<long>(src));
    }
};

template<> struct type_caster<FileTypes>
{
  public:
    PYBIND11_TYPE_CASTER(FileTypes, _("FileTypes"));

    bool
    load(handle src, bool)
    {
        if (!src || !PyLong_Check(src.ptr()))
        {
            return false;
        }
        value = static_cast<FileTypes>(PyLong_AsLong(src.ptr()));
        return true;
    }

    static handle
    cast(FileTypes src, return_value_policy, handle)
    {
        return PyLong_FromLong(static_cast<long>(src));
    }
};

template<> struct type_caster<Scroll>
{
  public:
    PYBIND11_TYPE_CASTER(Scroll, _("Scroll"));

    bool
    load(handle src, bool)
    {
        if (!src || !PyLong_Check(src.ptr()))
        {
            return false;
        }
        value = static_cast<Scroll>(PyLong_AsLong(src.ptr()));
        return true;
    }

    static handle
    cast(Scroll src, return_value_policy, handle)
    {
        return PyLong_FromLong(static_cast<long>(src));
    }
};

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

template<> struct type_caster<ZoomAxis>
{
  public:
    PYBIND11_TYPE_CASTER(ZoomAxis, _("ZoomAxis"));

    bool
    load(handle src, bool)
    {
        if (!src || !PyLong_Check(src.ptr()))
        {
            return false;
        }
        value = static_cast<ZoomAxis>(PyLong_AsLong(src.ptr()));
        return true;
    }

    static handle
    cast(ZoomAxis src, return_value_policy, handle)
    {
        return PyLong_FromLong(static_cast<long>(src));
    }
};
} // namespace pybind11::detail

namespace py = pybind11;

PYBIND11_MODULE(mcomix_compiled, m)
{
    py::enum_<Animation>(m, "Animation")
        .value("DISABLED", Animation::DISABLED)
        .value("NORMAL", Animation::NORMAL)
        .export_values();

    py::enum_<ConfigType>(m, "ConfigType")
        .value("CONFIG", ConfigType::CONFIG)
        .value("KEYBINDINGS", ConfigType::KEYBINDINGS)
        .export_values();

    py::enum_<DialogChoice>(m, "DialogChoice")
        .value("ABOUT", DialogChoice::ABOUT)
        .value("ENHANCE", DialogChoice::ENHANCE)
        .value("FILECHOOSER", DialogChoice::FILECHOOSER)
        .value("KEYBINDINGS", DialogChoice::KEYBINDINGS)
        .value("PREFERENCES", DialogChoice::PREFERENCES)
        .value("PROPERTIES", DialogChoice::PROPERTIES)
        .export_values();

    py::enum_<DoublePage>(m, "DoublePage")
        .value("NEVER", DoublePage::NEVER)
        .value("AS_ONE_TITLE", DoublePage::AS_ONE_TITLE)
        .value("AS_ONE_WIDE", DoublePage::AS_ONE_WIDE)
        .value("ALWAYS", DoublePage::ALWAYS)
        .export_values();

    py::enum_<FileSortType>(m, "FileSortType")
        .value("NONE", FileSortType::NONE)
        .value("NAME", FileSortType::NAME)
        .value("SIZE", FileSortType::SIZE)
        .value("LAST_MODIFIED", FileSortType::LAST_MODIFIED)
        .value("NAME_LITERAL", FileSortType::NAME_LITERAL)
        .export_values();

    py::enum_<FileSortDirection>(m, "FileSortDirection")
        .value("DESCENDING", FileSortDirection::DESCENDING)
        .value("ASCENDING", FileSortDirection::ASCENDING)
        .export_values();

    py::enum_<FileTypes>(m, "FileTypes")
        .value("IMAGES", FileTypes::IMAGES)
        .value("ARCHIVES", FileTypes::ARCHIVES)
        .export_values();

    py::enum_<Scroll>(m, "Scroll")
        .value("END", Scroll::END)
        .value("START", Scroll::START)
        .value("CENTER", Scroll::CENTER)
        .export_values();

    py::enum_<ZoomModes>(m, "ZoomModes")
        .value("BEST", ZoomModes::BEST)
        .value("WIDTH", ZoomModes::WIDTH)
        .value("HEIGHT", ZoomModes::HEIGHT)
        .value("MANUAL", ZoomModes::MANUAL)
        .value("SIZE", ZoomModes::SIZE)
        .export_values();

    py::enum_<ZoomAxis>(m, "ZoomAxis")
        .value("DISTRIBUTION", ZoomAxis::DISTRIBUTION)
        .value("ALIGNMENT", ZoomAxis::ALIGNMENT)
        .value("WIDTH", ZoomAxis::WIDTH)
        .value("HEIGHT", ZoomAxis::HEIGHT)
        .export_values();

    py::class_<PackageInfo>(m, "PackageInfo")
        .def_readonly_static("APP_NAME", &PackageInfo::APP_NAME)
        .def_readonly_static("PROG_NAME", &PackageInfo::PROG_NAME)
        .def_readonly_static("VERSION", &PackageInfo::VERSION);

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

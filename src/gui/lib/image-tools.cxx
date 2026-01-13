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

#include <filesystem>
#include <format>
#include <utility>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include <ztd/ztd.hxx>

#include "gui/lib/image-tools.hxx"

#include "logger.hxx"

#if defined(PIXBUF_BACKEND)

Glib::RefPtr<Gdk::Pixbuf>
gui::lib::image_tools::load_pixbuf(const std::filesystem::path& path) noexcept
{
    try
    {
        return Gdk::Pixbuf::create_from_file(path);
    }
    catch (const Glib::Error& ex)
    {
        logger::error<logger::gui>("Failed to load image: {} ", path.string());
        return nullptr;
    }
}

Glib::RefPtr<Gdk::Paintable>
gui::lib::image_tools::fit_to_rectangle(const Glib::RefPtr<Gdk::Pixbuf>& src,
                                        std::int32_t max_width, std::int32_t max_height,
                                        std::int32_t rotation) noexcept
{
    // return fit_to_rectangle(Gdk::Texture::create_for_pixbuf(src), max_width, max_height);

    static auto get_fitting_size = [](const std::int32_t src_width,
                                      const std::int32_t src_height,
                                      const std::int32_t max_width,
                                      const std::int32_t max_height) -> std::array<std::int32_t, 2>
    {
        const auto use_width =
            static_cast<std::int64_t>(src_width) * static_cast<std::int64_t>(max_height) >
            static_cast<std::int64_t>(max_width) * static_cast<std::int64_t>(src_height);

        if (use_width)
        {
            return {max_width, std::max(1, (src_height * max_width) / src_width)};
        }
        else
        {
            return {std::max(1, (src_width * max_height) / src_height), max_height};
        }
    };

    const auto is_sideways = (rotation == 90 || rotation == 270);
    if (is_sideways)
    {
        std::swap(max_width, max_height);
    }

    const auto src_width = src->get_width();
    const auto src_height = src->get_height();

    const auto [new_width, new_height] =
        get_fitting_size(src_width, src_height, max_width, max_height);

    // logger::info<logger::gui>("new {}x{} | src {}x{}", new_width, new_height, src_width, src_height);

    Glib::RefPtr<Gdk::Pixbuf> new_pixbuf;
    if (src->get_has_alpha())
    {
        new_pixbuf = src->composite_color_simple(new_width,
                                                 new_height,
                                                 Gdk::InterpType::BILINEAR,
                                                 255,
                                                 16,
                                                 0x777777,
                                                 0x999999);
    }
    else if (new_width != src_width || new_height != src_height)
    {
        new_pixbuf = src->scale_simple(new_width, new_height, Gdk::InterpType::BILINEAR);
    }
    else
    {
        new_pixbuf = src;
    }

    switch (rotation)
    {
        case 0:
            return Gdk::Texture::create_for_pixbuf(new_pixbuf);
        case 90:
            return Gdk::Texture::create_for_pixbuf(
                new_pixbuf->rotate_simple(Gdk::Pixbuf::Rotation::CLOCKWISE));
        case 180:
            return Gdk::Texture::create_for_pixbuf(
                new_pixbuf->rotate_simple(Gdk::Pixbuf::Rotation::UPSIDEDOWN));
        case 270:
            return Gdk::Texture::create_for_pixbuf(
                new_pixbuf->rotate_simple(Gdk::Pixbuf::Rotation::COUNTERCLOCKWISE));
        default:
            std::unreachable();
    }
}

#else

Glib::RefPtr<Gdk::Texture>
gui::lib::image_tools::load_texture(const std::filesystem::path& path) noexcept
{
    try
    {
        return Gdk::Texture::create_from_filename(path);
    }
    catch (const Glib::Error& ex)
    {
        logger::error<logger::gui>("Failed to load image: {} ", path.string());
        return nullptr;
    }
}

Glib::RefPtr<Gdk::Paintable>
gui::lib::image_tools::fit_to_rectangle(const Glib::RefPtr<Gdk::Texture>& src,
                                        std::int32_t max_width, std::int32_t max_height,
                                        std::int32_t rotation) noexcept
{
    const auto is_sideways = (rotation == 90 || rotation == 270);
    if (is_sideways)
    {
        std::swap(max_width, max_height);
    }

    const auto src_width = static_cast<std::float_t>(src->get_width());
    const auto src_height = static_cast<std::float_t>(src->get_height());

    const auto scale = std::min(static_cast<std::float_t>(max_width) / src_width,
                                static_cast<std::float_t>(max_height) / src_height);

    const auto scaled_width = src_width * scale;
    const auto scaled_height = src_height * scale;

    const auto final_width = is_sideways ? scaled_height : scaled_width;
    const auto final_height = is_sideways ? scaled_width : scaled_height;

    // logger::info<logger::gui>("new {}x{} | src {}x{}", final_width, final_height, src_width, src_height);

    auto snapshot = Gtk::Snapshot::create();

    switch (rotation)
    {
        case 0:
            break;
        case 90:
            snapshot->translate(Gdk::Graphene::Point(final_width, 0.0f));
            snapshot->rotate(90.0f);
            break;
        case 180:
            snapshot->translate(Gdk::Graphene::Point(final_width, final_height));
            snapshot->rotate(180.0f);
            break;
        case 270:
            snapshot->translate(Gdk::Graphene::Point(0.0f, final_height));
            snapshot->rotate(270.0f);
            break;
        default:
            std::unreachable();
    }

    snapshot->scale(scale, scale);
    snapshot->append_texture(src, Gdk::Graphene::Rect(0.0f, 0.0f, src_width, src_height));

    return snapshot->to_paintable(Gdk::Graphene::Size(final_width, final_height));
}

#endif

Glib::RefPtr<Gdk::Paintable>
gui::lib::image_tools::create_thumbnail(const std::filesystem::path& path,
                                        std::int32_t size) noexcept
{
#if defined(PIXBUF_BACKEND)
    auto image = gui::lib::image_tools::load_pixbuf(path);
#else
    auto image = gui::lib::image_tools::load_texture(path);
#endif
    if (!image)
    {
        return nullptr;
    }

    return create_thumbnail(image, size);
}

#if defined(PIXBUF_BACKEND)

[[nodiscard]] Glib::RefPtr<Gdk::Paintable>
gui::lib::image_tools::create_thumbnail(const Glib::RefPtr<Gdk::Pixbuf>& src,
                                        std::int32_t size) noexcept
{
    // return create_thumbnail(Gdk::Texture::create_for_pixbuf(src), size);
    return fit_to_rectangle(src, size, size);
}

#else

[[nodiscard]] Glib::RefPtr<Gdk::Paintable>
gui::lib::image_tools::create_thumbnail(const Glib::RefPtr<Gdk::Texture>& src,
                                        std::int32_t size) noexcept
{
    return fit_to_rectangle(src, size, size);
}

#endif

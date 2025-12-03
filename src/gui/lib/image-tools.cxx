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

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include <ztd/ztd.hxx>

#include "gui/lib/image-tools.hxx"

#include "logger.hxx"

Glib::RefPtr<Gdk::Pixbuf>
gui::lib::image_tools::rotate_pixbuf(const Glib::RefPtr<Gdk::Pixbuf>& src,
                                     std::int32_t rotation) noexcept
{
    switch (rotation)
    {
        case 0:
            return src->rotate_simple(Gdk::Pixbuf::Rotation::NONE);
        case 90:
            return src->rotate_simple(Gdk::Pixbuf::Rotation::CLOCKWISE);
        case 180:
            return src->rotate_simple(Gdk::Pixbuf::Rotation::UPSIDEDOWN);
        case 270:
            return src->rotate_simple(Gdk::Pixbuf::Rotation::COUNTERCLOCKWISE);
        default:
            logger::error("bad rotation value: {}", rotation);
            return src->rotate_simple(Gdk::Pixbuf::Rotation::NONE);
    }
}

std::array<std::int32_t, 2>
gui::lib::image_tools::get_fitting_size(const std::int32_t src_width, const std::int32_t src_height,
                                        std::int32_t width, std::int32_t height,
                                        const bool scale_up) noexcept
{
    if (!scale_up && src_width <= width && src_height <= height)
    {
        return {width, height};
    }

    if ((src_width / width) > (src_height / height))
    {
        height = std::max(src_height * width / src_width, 1);
    }
    else
    {
        width = std::max(src_width * height / src_height, 1);
    }
    return {width, height};
}

Glib::RefPtr<Gdk::Pixbuf>
gui::lib::image_tools::add_alpha_background(const Glib::RefPtr<Gdk::Pixbuf>& pixbuf,
                                            const std::int32_t width,
                                            const std::int32_t height) noexcept
{
    const auto check_size = 16;
    const auto color1 = 0x777777;
    const auto color2 = 0x999999;

    return pixbuf->composite_color_simple(width,
                                          height,
                                          Gdk::InterpType::BILINEAR,
                                          255,
                                          check_size,
                                          color1,
                                          color2);
}

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
gui::lib::image_tools::fit_to_rectangle(const Glib::RefPtr<Gdk::Pixbuf>& src, std::int32_t width,
                                        std::int32_t height, std::int32_t rotation) noexcept
{
    // logger::info<logger::gui>("new {}x{}", width, height);

    if (rotation == 90 || rotation == 270)
    {
        std::swap(width, height);
    }

    const auto src_width = src->get_width();
    const auto src_height = src->get_height();

    const auto [new_width, new_height] =
        get_fitting_size(src_width, src_height, width, height, true);

    // logger::info<logger::gui>("new {}x{} | src {}x{}", new_width, new_height, src_width, src_height);

    Glib::RefPtr<Gdk::Pixbuf> new_pixbuf;
    if (src->get_has_alpha())
    {
        new_pixbuf = add_alpha_background(src, new_width, new_height);
    }
    else if (new_width != src_width || new_height != src_height)
    {
        new_pixbuf = src->scale_simple(new_width, new_height, Gdk::InterpType::BILINEAR);
    }
    else
    {
        new_pixbuf = src;
    }

    return Gdk::Texture::create_for_pixbuf(rotate_pixbuf(new_pixbuf, rotation));
}

Glib::RefPtr<Gdk::Paintable>
gui::lib::image_tools::create_thumbnail(const std::filesystem::path& path,
                                        std::int32_t size) noexcept
{
    auto pixbuf = gui::lib::image_tools::load_pixbuf(path);
    if (!pixbuf)
    {
        return nullptr;
    }

    return create_thumbnail(pixbuf, size);
}

[[nodiscard]] Glib::RefPtr<Gdk::Paintable>
gui::lib::image_tools::create_thumbnail(const Glib::RefPtr<Gdk::Pixbuf>& src,
                                        std::int32_t size) noexcept
{
    const auto src_width = src->get_width();
    const auto src_height = src->get_height();

    const auto [new_width, new_height] = get_fitting_size(src_width, src_height, size, size, false);

    return fit_to_rectangle(src, new_width, new_height);
}

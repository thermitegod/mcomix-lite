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

#include <algorithm>
#include <filesystem>
#include <format>
#include <utility>
#include <vector>

#include <cmath>
#include <cstdint>

#include <cairomm/cairomm.h>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

#include <ztd/ztd.hxx>

#include "vfs/image-tools/image-tools.hxx"

#include "glycin/glycin.hxx"
#include "logger.hxx"

Glib::RefPtr<Gly::Image>
vfs::image_tools::load_image(const std::filesystem::path& path) noexcept
{
    // logger::info<logger::gui>("Loading '{}'", path);

    auto file = Gio::File::create_for_path(path);

    try
    {
        auto loader = Gly::Loader::create(file);
        auto image = loader->load();

        return image;
    }
    catch (const Glib::Error& e)
    {
        logger::error<logger::gui>("Loading '{}' failed with: {}", file->get_path(), e.what());
        return nullptr;
    }
}

Glib::RefPtr<Gdk::Texture>
vfs::image_tools::load_texture(const std::filesystem::path& path) noexcept
{
    auto file = Gio::File::create_for_path(path);

    try
    {
        auto loader = Gly::Loader::create(file);
        auto image = loader->load();
        auto frame = image->next_frame();
        auto texture = frame->get_texture();

        return texture;
    }
    catch (const Glib::Error& e)
    {
        logger::error<logger::gui>("Loading '{}' failed with: {}", file->get_path(), e.what());
        return nullptr;
    }
}

Glib::RefPtr<Gdk::Paintable>
vfs::image_tools::fit_to_rectangle(const Glib::RefPtr<Gly::Image>& src, std::int32_t max_width,
                                   std::int32_t max_height, std::int32_t rotation) noexcept
{
    const bool is_sideways = (rotation == 90 || rotation == 270);

    const auto src_width = static_cast<std::float_t>(src->get_width());
    const auto src_height = static_cast<std::float_t>(src->get_height());

    const auto target_width = static_cast<std::float_t>(is_sideways ? max_height : max_width);
    const auto target_height = static_cast<std::float_t>(is_sideways ? max_width : max_height);

    const auto scale = std::min(target_width / src_width, target_height / src_height);

    const auto final_width = src_width * scale;
    const auto final_height = src_height * scale;

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
    snapshot->append_texture(src->next_frame()->get_texture(),
                             Gdk::Graphene::Rect(0.0f, 0.0f, src_width, src_height));

    return snapshot->to_paintable(Gdk::Graphene::Size(final_width, final_height));
}

Glib::RefPtr<Gdk::Paintable>
vfs::image_tools::create_thumbnail(const std::filesystem::path& path, std::int32_t size) noexcept
{
    auto image = vfs::image_tools::load_image(path);
    if (!image)
    {
        return nullptr;
    }

    return create_thumbnail(image, size);
}

static Glib::RefPtr<Gdk::Texture>
texture_downsample(const Glib::RefPtr<Gdk::Texture>& src, std::int32_t max_width,
                   std::int32_t max_height) noexcept
{
    const auto src_width = src->get_width();
    const auto src_height = src->get_height();

    const auto scale =
        std::min(static_cast<std::float_t>(max_width) / static_cast<std::float_t>(src_width),
                 static_cast<std::float_t>(max_height) / static_cast<std::float_t>(src_height));

    const auto final_width =
        static_cast<std::int32_t>(std::lround(static_cast<std::float_t>(src_width) * scale));
    const auto final_height =
        static_cast<std::int32_t>(std::lround(static_cast<std::float_t>(src_height) * scale));

    // logger::info<logger::gui>("down {}x{} | src {}x{}", final_width, final_height, src_width, src_height);

    const auto src_stride = src_width * 4;
    std::vector<std::uint8_t> src_pixels(static_cast<std::size_t>(src_stride * src_height));

    src->download(src_pixels.data(), static_cast<std::size_t>(src_stride));

    auto src_surface = Cairo::ImageSurface::create(src_pixels.data(),
                                                   Cairo::Surface::Format::ARGB32,
                                                   src_width,
                                                   src_height,
                                                   src_stride);

    auto pattern = Cairo::SurfacePattern::create(src_surface);
    pattern->set_filter(Cairo::SurfacePattern::Filter::GOOD);

    auto surface =
        Cairo::ImageSurface::create(Cairo::Surface::Format::ARGB32, final_width, final_height);
    auto cr = Cairo::Context::create(surface);
    cr->scale(scale, scale);
    cr->set_source(pattern);
    cr->paint();

    surface->flush();

    const auto stride = surface->get_stride();
    auto bytes =
        Glib::Bytes::create(surface->get_data(), static_cast<std::size_t>(stride * final_height));

    return Gdk::MemoryTexture::create(final_width,
                                      final_height,
                                      Gdk::MemoryTexture::Format::B8G8R8A8_PREMULTIPLIED,
                                      bytes,
                                      static_cast<std::size_t>(stride));
}

Glib::RefPtr<Gdk::Paintable>
vfs::image_tools::create_thumbnail(const Glib::RefPtr<Gly::Image>& src, std::int32_t size) noexcept
{
    return texture_downsample(src->next_frame()->get_texture(), size, size);
}

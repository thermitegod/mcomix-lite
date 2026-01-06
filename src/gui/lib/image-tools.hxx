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

#pragma once

#include <filesystem>

#include <gdkmm.h>
#include <glibmm.h>
#include <gtkmm.h>

namespace gui::lib::image_tools
{
/**
 * Loads a pixbuf from a given image file.
 *
 * @param path: Path to the image file.
 * @returns: A new pixbuf or nullptr on failure.
 */
[[nodiscard]] Glib::RefPtr<Gdk::Pixbuf> load_pixbuf(const std::filesystem::path& path) noexcept;
[[nodiscard]] Glib::RefPtr<Gdk::Texture> load_texture(const std::filesystem::path& path) noexcept;

[[nodiscard]] Glib::RefPtr<Gdk::Paintable> fit_to_rectangle(const Glib::RefPtr<Gdk::Pixbuf>& pixbuf,
                                                            std::int32_t max_width,
                                                            std::int32_t max_height,
                                                            std::int32_t rotation = 0) noexcept;

[[nodiscard]] Glib::RefPtr<Gdk::Paintable> fit_to_rectangle(const Glib::RefPtr<Gdk::Texture>& src,
                                                            std::int32_t max_width,
                                                            std::int32_t max_height,
                                                            std::int32_t rotation = 0) noexcept;

/**
 * Returns a thumbnail pixbuf for a given path.
 * Transparently handles both normal image files and archives.
 *
 * @param path: Path to the image for thumbnail creation.
 * @param size: Maximum size of any one side of the created thumbnails.
 * @returns: A new thumbnail pixbuf or nullptr on failure.
 */
[[nodiscard]] Glib::RefPtr<Gdk::Paintable> create_thumbnail(const std::filesystem::path& path,
                                                            std::int32_t size) noexcept;

[[nodiscard]] Glib::RefPtr<Gdk::Paintable> create_thumbnail(const Glib::RefPtr<Gdk::Pixbuf>& pixbuf,
                                                            std::int32_t size) noexcept;

[[nodiscard]] Glib::RefPtr<Gdk::Paintable>
create_thumbnail(const Glib::RefPtr<Gdk::Texture>& texture, std::int32_t size) noexcept;
} // namespace gui::lib::image_tools

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
 * Rotates the pixbuf by a given angle.
 *
 * @param src: Source pixbuf to rotate.
 * @param rotation: Rotation angle in degrees (0, 90, 180, 270).
 * @returns: A new rotated pixbuf.
 */
[[nodiscard]] Glib::RefPtr<Gdk::Pixbuf> rotate_pixbuf(const Glib::RefPtr<Gdk::Pixbuf>& src,
                                                      std::int32_t rotation) noexcept;

/**
 * Return a scaled version of source size small enough to fit in target size.
 * Both source size and target size must be (width, height) tuples.
 * If keep_ratio is True, aspect ratio is kept.
 * If scale_up is True, source size is scaled up when smaller than target size.
 *
 * @param src_width: Source image width.
 * @param src_height: Source image height.
 * @param width: Target width.
 * @param height: Target height.
 * @param keep_ratio: Maintain aspect ratio.
 * @param scale_up: Allow scaling up.
 * @returns: A pair containing the adjusted width and height.
 */
[[nodiscard]] std::array<std::int32_t, 2> get_fitting_size(const std::int32_t src_width,
                                                           const std::int32_t src_height,
                                                           std::int32_t width, std::int32_t height,
                                                           const bool keep_ratio = true,
                                                           const bool scale_up = false) noexcept;

/**
 * Adds a checkerboard background to a pixbuf with an alpha channel.
 *
 * @param pixbuf: Source pixbuf with an alpha channel.
 * @param width: Width of the new pixbuf.
 * @param height: Height of the new pixbuf.
 * @returns: A new pixbuf with a checkerboard background.
 */
[[nodiscard]] Glib::RefPtr<Gdk::Pixbuf>
add_alpha_background(const Glib::RefPtr<Gdk::Pixbuf>& pixbuf, const std::int32_t width,
                     const std::int32_t height) noexcept;

/**
 * Scale (and return) a pixbuf so that it fits in a rectangle with dimensions <width> x <height>.
 * If rotation is 90, 180, or 270, rotates src first so that the rotated pixbuf fits in the rectangle.
 *
 * @param src: Source pixbuf to fit.
 * @param width: Target width.
 * @param height: Target height.
 * @param keep_ratio: Maintain aspect ratio.
 * @param scale_up: Allow scaling up.
 * @param rotation: Rotation angle (0, 90, 180, 270).
 * @returns: A new pixbuf scaled and rotated to fit within the target dimensions.
 */
[[nodiscard]] Glib::RefPtr<Gdk::Pixbuf>
fit_in_rectangle(const Glib::RefPtr<Gdk::Pixbuf>& src, std::int32_t width, std::int32_t height,
                 bool keep_ratio = true, bool scale_up = false, std::int32_t rotation = 0) noexcept;

/**
 * Return a pixbuf from the source with a black 1 px border.
 *
 * @param pixbuf: Source pixbuf.
 * @returns: A new pixbuf with a 1 px black border.
 */
[[nodiscard]] Glib::RefPtr<Gdk::Pixbuf>
add_border_pixbuf(const Glib::RefPtr<Gdk::Pixbuf>& pixbuf) noexcept;

[[nodiscard]] bool disable_transform(const Glib::RefPtr<Gdk::Pixbuf>& pixbuf) noexcept;

void set_from_pixbuf(Gtk::Picture& picture, const Glib::RefPtr<Gdk::Pixbuf>& pixbuf) noexcept;

/**
 * Loads a pixbuf from a given image file.
 *
 * @param path: Path to the image file.
 * @returns: A new pixbuf or nullptr on failure.
 */
[[nodiscard]] Glib::RefPtr<Gdk::Pixbuf> load_pixbuf(const std::filesystem::path& path) noexcept;

[[nodiscard]] Glib::RefPtr<Gdk::Pixbuf>
fit_pixbuf_to_rectangle(const Glib::RefPtr<Gdk::Pixbuf>& pixbuf, std::int32_t width,
                        std::int32_t height, std::int32_t rotation = 0) noexcept;

/**
 * Returns a thumbnail pixbuf for a given path.
 * Transparently handles both normal image files and archives.
 *
 * @param path: Path to the image for thumbnail creation.
 * @param size: Maximum size of any one side of the created thumbnails.
 * @returns: A new thumbnail pixbuf or nullptr on failure.
 */
[[nodiscard]] Glib::RefPtr<Gdk::Pixbuf> create_thumbnail(const std::filesystem::path& path,
                                                         std::int32_t size) noexcept;
} // namespace gui::lib::image_tools

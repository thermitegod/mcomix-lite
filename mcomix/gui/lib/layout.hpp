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

#include <array>
#include <vector>

#include <cstdint>

#include "box.hpp"

class Layout
{
  public:
    Layout() = default;

    /**
     * Lays out a finite number of Boxes along the first axis.
     *
     * @param content_sizes: The sizes of the Boxes to lay out.
     * @param viewport_size: The size of the viewport.
     * @param orientation: The orientation to use.
     * @param distribution_axis: The axis along which the Boxes are distributed.
     * @param alignment_axis: The axis to center.
     */
    Layout(std::vector<std::array<std::int32_t, 2>> content_sizes, const std::array<std::int32_t, 2>& viewport_size,
           const std::array<std::int32_t, 2>& orientation, const std::int32_t distribution_axis,
           const std::int32_t alignment_axis);

    /**
     * Returns a new viewport position when scrolling towards a predefined destination.
     *
     * @param destination: An integer representing a predefined destination.
     * Either 1 (towards the greatest possible values in this dimension),
     * -1 (towards the smallest value in this dimension), 0 (keep position),
     * SCROLL_TO_CENTER (scroll to the center of the content in this dimension),
     * SCROLL_TO_START (scroll to where the content starts in this dimension),
     * or SCROLL_TO_END (scroll to where the content ends in this dimension).
     * @returns: A new viewport position as specified above.
     */
    void scroll_to_predefined(const std::array<std::int32_t, 2>& destination);

    /**
     * Returns the Boxes as they are arranged in this layout.
     *
     * @returns: The Boxes as they are arranged in this layout.
     */
    [[nodiscard]] std::vector<Box> get_content_boxes() const noexcept;

    /**
     * Returns the union Box for this layout.
     *
     * @return: The union Box for this layout.
     */
    [[nodiscard]] Box get_union_box() const noexcept;

    /**
     * Returns the current viewport Box.
     *
     * @returns: The current viewport Box.
     */
    [[nodiscard]] Box get_viewport_box() const noexcept;

    /**
     * Returns the current orientation Box.
     *
     * @returns: The current orientation.
     */
    [[nodiscard]] const std::array<std::int32_t, 2> get_orientation() const noexcept;

    void set_orientation(const std::array<std::int32_t, 2>& new_orientation);

  private:
    std::vector<Box> content_boxes_;
    Box union_box_;
    Box viewport_box_;
    std::array<std::int32_t, 2> orientation_;
};

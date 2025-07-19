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

#include <vector>
#include <cstdint>

class Box
{
  public:
    Box() = default;

    /*
     * A Box is immutable and always axis-aligned.
     * Each component of size should be positive (i.e. non-zero).
     * Both position and size must have equal number of dimensions.
     * If there is only one argument, it must be the size. In this case, the
     * position is set to origin (i.e. all coordinates are 0) by definition.
     *
     * :param position: The position of this Box.
     * :param size: The size of this Box
     */
    Box(const std::vector<std::int32_t>& position, const std::vector<std::int32_t>& size = {});

    /*
     * Two Boxes are said to be equal if and only if the number of
     * dimensions, the positions and the sizes of the two Boxes are equal, respectively
     */
    bool
    operator==(const Box& other) const noexcept
    {
        return (this->position_ == other.position_) && (this->size_ == other.size_);
        // return (this->get_position() == other.get_position()) && (this->get_size() == other.get_size());
    }

    // the number of dimensions of this Box
    [[nodiscard]] std::size_t dimensions() const noexcept;

    // the size of this Box
    [[nodiscard]] std::vector<std::int32_t> get_size() const noexcept;

    //  the position of this Box
    [[nodiscard]] std::vector<std::int32_t> get_position() const noexcept;

    /*
     * a new Box that has the same size as this Box and the specified position
     *
     * :return: A new Box as specified above
     */
    [[nodiscard]] Box set_position(const std::vector<std::int32_t>& new_position) const noexcept;

    /*
     * Returns a new Box that has the same size as this Box and a
     * oppositely translated position as specified by delta.
     * :param delta: The distance to the position of this Box, with opposite direction.
     * :return: A new Box as specified above
     */
    [[nodiscard]] Box translate_opposite(const std::vector<std::int32_t>& delta) const noexcept;

    [[nodiscard]] static std::int32_t box_to_center_offset_1d(std::int32_t box_size_delta,
                                                              const std::int32_t orientation) noexcept;

    /*
     * Aligns Boxes so that the center of each Box appears on the same line.
     *
     * :param boxes: boxes
     * :param axis: the axis to center.
     * :param fix: the index of the Box that should not move.
     * :param orientation: The orientation to use.
     * :returns: A list of new Boxes with accordingly translated positions
     */
    [[nodiscard]] static std::vector<Box> align_center(const std::vector<Box>& boxes, const std::int32_t axis,
                                                       const std::int32_t fix, const std::int32_t orientation) noexcept;

    /*
     * Ensures that the Boxes do not overlap. For this purpose, the Boxes
     * are distributed according to the index of the respective Box.
     *
     * :param boxes: boxes
     * :param axis: the axis along which the Boxes are distributed.
     * :param fix: the index of the Box that should not move.
     * :param spacing: the number of additional pixels between Boxes.
     * :returns: A new list with new Boxes that are accordingly translated
     */
    [[nodiscard]] static std::vector<Box> distribute(const std::vector<Box>& boxes, const std::int32_t axis,
                                                     const std::int32_t fix, const std::int32_t spacing = 2) noexcept;

    /*
     * Returns a Box that covers the same area that is covered by a
     * scrollable viewport showing this Box.
     *
     * :param viewport_size: The size of the viewport.
     * :param orientation: The orientation to use.
     * :returns: A Box as specified above
     */
    [[nodiscard]] Box wrapper_box(const std::vector<std::int32_t>& viewport_size,
                                  const std::array<std::int32_t, 2>& orientation) const noexcept;

    /*
     * Returns the union of all specified Boxes (that is, the smallest Box
     * that contains all specified Boxes).=
     * :param boxes: The Boxes to calculate the union from.
     * :returns: A Box as specified above
     */
    [[nodiscard]] static Box bounding_box(const std::vector<Box>& boxes) noexcept;

  private:
    std::vector<std::int32_t> position_;
    std::vector<std::int32_t> size_;
};

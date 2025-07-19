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

#include <array>
#include <vector>

#include <ranges>
#include <algorithm>

#include <cassert>

#include "box.hpp"
#include "enums.hpp"
#include "layout.hpp"

Layout::Layout(std::vector<std::array<std::int32_t, 2>> content_sizes, const std::array<std::int32_t, 2>& viewport_size,
               const std::array<std::int32_t, 2>& orientation, const ZoomAxis distribution_axis,
               const ZoomAxis alignment_axis)
{
    // Reverse order if necessary
    if (orientation[static_cast<std::int32_t>(distribution_axis)] == -1)
    {
        std::ranges::reverse(content_sizes);
    }

    for (const auto& size : content_sizes)
    {
        this->content_boxes_.emplace_back(Box({size[0], size[1]}));
    }

    // Align to center
    this->content_boxes_ = Box::align_center(this->content_boxes_,
                                             static_cast<std::int32_t>(alignment_axis),
                                             0,
                                             orientation[static_cast<std::int32_t>(alignment_axis)]);

    // Distribute
    this->content_boxes_ = Box::distribute(this->content_boxes_, static_cast<std::int32_t>(distribution_axis), 0);
    this->union_box_ =
        Box::bounding_box(this->content_boxes_).wrapper_box({viewport_size[0], viewport_size[1]}, orientation);

    // Move to global origin
    const auto bbp = this->union_box_.get_position();
    for (const auto [idx, box] : std::ranges::views::enumerate(this->content_boxes_))
    {
        (void)box;
        this->content_boxes_[idx] = this->content_boxes_[idx].translate_opposite(bbp);
    }

    this->union_box_ = this->union_box_.translate_opposite(bbp);
    // Reverse order again, if necessary
    if (orientation[static_cast<std::int32_t>(distribution_axis)] == -1)
    {
        std::ranges::reverse(this->content_boxes_);
    }

    this->viewport_box_ = Box({viewport_size[0], viewport_size[1]});
    this->orientation_ = orientation;
}

void
Layout::scroll_to_predefined(const std::array<Scroll, 2>& destination)
{
    const auto content_position = this->union_box_.get_position();
    const auto content_size = this->union_box_.get_size();
    const auto viewport_size = this->viewport_box_.get_size();
    auto result = this->viewport_box_.get_position();

    for (std::size_t idx = 0; idx < content_size.size(); ++idx)
    {
        std::int32_t o = this->orientation_[idx];
        std::int32_t d = static_cast<std::int32_t>(destination[idx]);

        if (d == 0)
        {
            continue;
        }

        if (d == static_cast<std::int32_t>(Scroll::END))
        {
            d = static_cast<std::int32_t>(o);
        }
        else if (d == static_cast<std::int32_t>(Scroll::START))
        {
            d = -o;
        }

        std::int32_t c = content_size[idx];
        std::int32_t v = viewport_size[idx];
        std::int32_t invisible_size = c - v;
        std::int32_t offset;

        if (d == static_cast<std::int32_t>(Scroll::CENTER))
        {
            offset = Box::box_to_center_offset_1d(invisible_size, o);
        }
        else
        {
            offset = (d == 1) ? invisible_size : 0;
        }

        result[idx] = content_position[idx] + offset;
    }

    // Move the viewport to the specified position
    this->viewport_box_ = this->viewport_box_.set_position(result);
}

std::vector<Box>
Layout::get_content_boxes() const noexcept
{
    return this->content_boxes_;
}

Box
Layout::get_union_box() const noexcept
{
    return this->union_box_;
}

Box
Layout::get_viewport_box() const noexcept
{
    return this->viewport_box_;
}

const std::array<std::int32_t, 2>
Layout::get_orientation() const noexcept
{
    return this->orientation_;
}

void
Layout::set_orientation(const std::array<std::int32_t, 2>& new_orientation)
{
    this->orientation_ = new_orientation;
}

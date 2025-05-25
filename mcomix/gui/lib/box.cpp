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

#include <format>

#include <vector>

#include <algorithm>
#include <functional>

#include <stdexcept>

#include <cassert>

#include "box.hpp"

Box::Box(const std::vector<std::int32_t>& position, const std::vector<std::int32_t>& size)
{
    if (size.empty())
    {
        this->position_ = {0, 0};
        this->size_ = position;
    }
    else
    {
        this->position_ = position;
        this->size_ = size;
    }

    if (this->position_.size() != this->size_.size())
    {
        throw std::invalid_argument(
            std::format("Box has different dimensions: {} != {}", this->position_.size(), this->size_.size()));
    }
}

std::size_t
Box::dimensions() const noexcept
{
    return this->position_.size();
}

std::vector<std::int32_t>
Box::get_size() const noexcept
{
    return this->size_;
}

std::vector<std::int32_t>
Box::get_position() const noexcept
{
    return this->position_;
}

Box
Box::set_position(const std::vector<std::int32_t>& new_position) const noexcept
{
    return Box(new_position, this->size_);
}

Box
Box::translate_opposite(const std::vector<std::int32_t>& delta) const noexcept
{
    std::vector<std::int32_t> new_position(this->position_.size());
    std::transform(this->position_.cbegin(),
                   this->position_.cend(),
                   delta.cbegin(),
                   new_position.begin(),
                   std::minus<std::int32_t>());
    return Box(new_position, this->size_);
}

std::int32_t
Box::box_to_center_offset_1d(std::int32_t box_size_delta, const std::int32_t orientation) noexcept
{
    if (orientation == -1)
    {
        box_size_delta += 1;
    }
    return box_size_delta >> 1;
}

std::vector<Box>
Box::align_center(const std::vector<Box>& boxes, const std::int32_t axis, const std::int32_t fix,
                  const std::int32_t orientation) noexcept
{
    if (boxes.empty())
    {
        return {};
    }

    Box center_box = boxes[fix];
    auto cs = center_box.get_size()[axis];
    if (cs % 2 != 0)
    {
        cs += 1;
    }

    const auto cp = center_box.get_position()[axis];
    std::vector<Box> result;
    for (const auto& b : boxes)
    {
        auto s = b.get_size();
        auto p = b.get_position();
        p[axis] = cp + box_to_center_offset_1d(cs - s[axis], orientation);
        result.push_back(Box(p, s));
    }
    return result;
}

std::vector<Box>
Box::distribute(const std::vector<Box>& boxes, const std::int32_t axis, const std::int32_t fix,
                const std::int32_t spacing) noexcept
{
    if (boxes.empty())
    {
        return {};
    }

    std::vector<Box> result(boxes.size());

    auto initial_sum = boxes[fix].get_position()[axis];
    auto partial_sum = initial_sum;

    for (std::size_t bi = fix; bi < boxes.size(); ++bi)
    {
        Box b = boxes[bi];
        auto s = b.get_size();
        auto p = b.get_position();
        p[axis] = partial_sum;
        result[bi] = Box(p, s);
        partial_sum += s[axis] + spacing;
    }

    partial_sum = initial_sum;
    for (auto bi = fix - 1; bi >= 0; --bi)
    {
        Box b = boxes[bi];
        auto s = b.get_size();
        auto p = b.get_position();
        partial_sum -= s[axis] + spacing;
        p[axis] = partial_sum;
        result[bi] = Box(p, s);
    }

    return result;
}

Box
Box::wrapper_box(const std::vector<std::int32_t>& viewport_size,
                 const std::array<std::int32_t, 2>& orientation) const noexcept
{
    std::vector<std::int32_t> result_size(this->size_.size());
    std::vector<std::int32_t> result_position(this->size_.size());

    for (std::size_t idx = 0; idx < this->size_.size(); ++idx)
    {
        const auto c = this->size_[idx];
        const auto v = viewport_size[idx];
        result_size[idx] = std::max(c, v);
        result_position[idx] = box_to_center_offset_1d(c - result_size[idx], orientation[idx]) + this->position_[idx];
    }

    return Box(result_position, result_size);
}

Box
Box::bounding_box(const std::vector<Box>& boxes) noexcept
{
    if (boxes.empty())
    {
        return Box({}, {});
    }

    std::vector<std::int32_t> mins(boxes[0].get_size().size(), std::numeric_limits<std::int32_t>::max());
    std::vector<std::int32_t> maxes(mins.size(), std::numeric_limits<std::int32_t>::min());

    for (const auto& b : boxes)
    {
        const auto s = b.get_size();
        const auto p = b.get_position();

        for (std::size_t idx = 0; idx < mins.size(); ++idx)
        {
            if (p[idx] < mins[idx])
            {
                mins[idx] = p[idx];
            }
            const auto ps = p[idx] + s[idx];
            if (ps > maxes[idx])
            {
                maxes[idx] = ps;
            }
        }
    }

    std::vector<std::int32_t> size(mins.size());
    std::transform(maxes.cbegin(), maxes.cend(), mins.cbegin(), size.begin(), std::minus<std::int32_t>());

    return Box(mins, size);
}

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

#include <vector>
#include <algorithm>
#include <numeric>
#include <functional>

#include <cmath>

#include <magic_enum/magic_enum.hpp>

#include "zoom.hpp"

// ZoomModel::ZoomModel(const std::shared_ptr<Settings>& settings) : settings(settings) {}

void
ZoomModel::set_fit_mode(ZoomModes fitmode) noexcept
{
    this->fitmode_ = fitmode;
}

void
ZoomModel::set_scale_up(const bool scale_up) noexcept
{
    this->scale_up_ = scale_up;
}

void
ZoomModel::set_user_zoom_log(const double zoom_log) noexcept
{
    this->user_zoom_log_ = std::clamp<double>(zoom_log, this->min_user_zoom_log_, this->max_user_zoom_log_);
}

void
ZoomModel::zoom_in() noexcept
{
    this->set_user_zoom_log(this->user_zoom_log_ + 1);
}

void
ZoomModel::zoom_out() noexcept
{
    this->set_user_zoom_log(this->user_zoom_log_ - 1);
}

void
ZoomModel::reset_user_zoom() noexcept
{
    this->set_user_zoom_log(this->identity_zoom_log_);
}

std::vector<double>
ZoomModel::scale(const std::array<std::int32_t, 2>& t, const double factor) const noexcept
{
    std::vector<double> result;
    for (const auto& x : t)
    {
        result.push_back(x * factor);
    }
    return result;
}

std::vector<std::array<std::int32_t, 2>>
ZoomModel::get_zoomed_size(const std::vector<std::array<std::int32_t, 2>>& image_sizes,
                           const std::array<std::int32_t, 2>& screen_size, const std::int32_t distribution_axis,
                           const std::vector<bool>& do_not_transform) const noexcept
{
    const auto fitted_image_sizes = this->fix_page_sizes(image_sizes, distribution_axis, do_not_transform);
    const auto union_size = this->union_size(fitted_image_sizes, distribution_axis);
    const auto limits = this->calc_limits(union_size, screen_size, this->fitmode_, this->scale_up_);

    const auto prefscale = this->preferred_scale(union_size, limits, distribution_axis);
    std::vector<double> preferred_scales;
    for (const auto dnt : do_not_transform)
    {
        preferred_scales.push_back(dnt ? this->identity_zoom_ : prefscale);
    }

    std::vector<std::array<std::int32_t, 2>> prescaled;
    for (std::size_t i = 0; i < fitted_image_sizes.size(); ++i)
    {
        const auto scaled = this->scale_image_size(fitted_image_sizes[i], preferred_scales[i]);

        std::array<std::int32_t, 2> prescaled_as_integer;
        std::ranges::transform(scaled,
                               prescaled_as_integer.begin(),
                               [](double d) { return static_cast<std::int32_t>(d); });

        prescaled.push_back(prescaled_as_integer);
    }
    const auto prescaled_union_size = this->union_size(prescaled, distribution_axis);

    bool other_preferences = false;
    for (std::size_t idx = 0; idx < limits.size(); ++idx)
    {
        if (static_cast<std::int32_t>(idx) == distribution_axis)
        {
            continue;
        }
        if (limits[idx] != -1)
        {
            other_preferences = true;
            break;
        }
    }

    if (limits[distribution_axis] != -1 &&
        (prescaled_union_size[distribution_axis] > screen_size[distribution_axis] || !other_preferences))
    {
        auto distributed_scales = this->scale_distributed(fitted_image_sizes,
                                                          distribution_axis,
                                                          limits[distribution_axis],
                                                          this->scale_up_,
                                                          do_not_transform);
        if (other_preferences)
        {
            for (std::size_t i = 0; i < preferred_scales.size(); ++i)
            {
                preferred_scales[i] = std::min(preferred_scales[i], distributed_scales[i]);
            }
        }
        else
        {
            preferred_scales = distributed_scales;
        }
    }

    if (!this->scale_up_)
    {
        for (auto& scale : preferred_scales)
        {
            scale = std::min(scale, this->identity_zoom_);
        }
    }

    double user_scale = std::pow(2.0f, this->user_zoom_log_ / this->user_zoom_log_scale1_);
    std::vector<std::array<std::int32_t, 2>> result;
    for (std::size_t idx = 0; idx < preferred_scales.size(); ++idx)
    {
        result.push_back(this->scale_image_size(fitted_image_sizes[idx],
                                                preferred_scales[idx] *
                                                    (do_not_transform[idx] ? this->identity_zoom_ : user_scale)));
    }

    return result;
}

double
ZoomModel::preferred_scale(const std::array<std::int32_t, 2>& image_size, const std::vector<std::int32_t>& limits,
                           const std::int32_t distribution_axis) const noexcept
{
    double min_scale = -1;
    for (std::size_t idx = 0; idx < limits.size(); ++idx)
    {
        if (static_cast<std::int32_t>(idx) == distribution_axis)
        {
            continue;
        }
        const auto limit = limits[idx];
        if (limit == -1)
        {
            continue;
        }
        double s = static_cast<double>(limit) / static_cast<double>(image_size[idx]);
        if (min_scale == -1 || s < min_scale)
        {
            min_scale = s;
        }
    }
    if (min_scale == -1)
    {
        min_scale = this->identity_zoom_;
    }
    return min_scale;
}

std::vector<std::int32_t>
ZoomModel::calc_limits(const std::array<std::int32_t, 2>& union_size, const std::array<std::int32_t, 2>& screen_size,
                       ZoomModes fitmode, const bool allow_upscaling) const noexcept
{
    const bool manual = fitmode == ZoomModes::MANUAL;
    if (fitmode == ZoomModes::BEST ||
        (manual && allow_upscaling &&
         std::ranges::all_of(union_size, [&, i = 0](float value) mutable { return value < screen_size[i++]; })))
    {
        return {screen_size[0], screen_size[1]};
    }

    std::vector<std::int32_t> result(screen_size.size(), -1);
    if (manual)
    {
        return result;
    }

    std::int32_t fixed_size = -1;

    // TODO - get config opts from python
    // if (fitmode == ZoomModes::SIZE)
    // {
    //     fitmode = this->settings->fit_to_size_mode;
    //     fixed_size = this->settings->fit_to_size_px;
    // }

    switch (fitmode)
    {
        case ZoomModes::WIDTH:
            result[magic_enum::enum_integer(ZoomAxis::WIDTH)] =
                fixed_size == -1 ? screen_size[magic_enum::enum_integer(ZoomAxis::WIDTH)] : fixed_size;
            break;
        case ZoomModes::HEIGHT:
            result[magic_enum::enum_integer(ZoomAxis::HEIGHT)] =
                fixed_size == -1 ? screen_size[magic_enum::enum_integer(ZoomAxis::HEIGHT)] : fixed_size;
            break;
        default:
            // logger::error("Cannot map fitmode to axis");
            break;
    }

    return result;
}

std::vector<double>
ZoomModel::scale_distributed(const std::vector<std::array<std::int32_t, 2>>& sizes, const std::int32_t axis,
                             const std::int32_t max_size, const bool allow_upscaling,
                             const std::vector<bool>& do_not_transform) const noexcept
{
    // Trivial cases first
    const auto n = sizes.size();
    if (n == 0)
    {
        return {};
    }
    if (n >= max_size)
    {
        // In this case, only one solution or only an approximation is available.
        // if n > max_size, the result won't fit into max_size.
        std::vector<double> result;
        for (const auto& size : sizes)
        {
            // FIXME ignores do_not_transform
            result.push_back(1.0f / size[axis]);
        }
        return result;
    }

    std::int32_t total_axis_size = 0;
    for (const auto& size : sizes)
    {
        total_axis_size += size[axis];
    }
    if (total_axis_size <= max_size && !allow_upscaling)
    {
        // Identity case
        return std::vector<double>(n, this->identity_zoom_);
    }

    // Non-trivial case

    // FIXME initial guess should take unscalable images into account
    const double scale = static_cast<double>(max_size) / total_axis_size;
    std::vector<std::vector<double>> scaling_data(n);
    total_axis_size = 0;

    // Collect some data needed for actual computations later
    for (std::size_t i = 0; i < n; ++i)
    {
        const auto& this_size = sizes[i];

        // Shortcut: If the size cannot be changed, accept the original size.
        if (do_not_transform[i])
        {
            total_axis_size += this_size[axis];
            scaling_data[i] = {this->identity_zoom_, this->identity_zoom_, 0.0f, this->identity_zoom_, 0.0f};
            continue;
        }

        // Initial guess: The current scale works for all tuples.
        const auto ideal = this->scale(this_size, scale);
        const auto ideal_vol = std::accumulate(ideal.cbegin(), ideal.cend(), 1.0f, std::multiplies<double>());

        // Let's use a dummy to compute the actual (rounded) size along axis
        // so we can rescale the rounded tuple with a better local_scale
        // later. This rescaling is necessary to ensure that the sizes in ALL
        // dimensions are monotonically scaled (with respect to local_scale).
        // A nice side effect of this is that it keeps the aspect ratio better.
        const auto dummy_approx = this->round_nonempty({ideal[axis]})[0];
        const auto local_scale = static_cast<double>(dummy_approx) / this_size[axis];
        total_axis_size += dummy_approx;
        const bool can_be_downscaled = dummy_approx > 1;

        double forced_scale = 0.0f;
        double forced_vol_err = 0.0f;
        if (can_be_downscaled)
        {
            const auto forced_size = dummy_approx - 1;
            forced_scale = static_cast<double>(forced_size) / this_size[axis];
            const auto forced_approx = this->scale_image_size(this_size, forced_scale);
            forced_vol_err =
                (std::accumulate(forced_approx.cbegin(), forced_approx.cend(), 1.0f, std::multiplies<double>()) -
                 ideal_vol) /
                ideal_vol;
        }

        scaling_data[i] = {local_scale,
                           static_cast<double>(ideal_vol),
                           static_cast<double>(can_be_downscaled),
                           forced_scale,
                           forced_vol_err};
    }

    // Now we need to find at most total_axis_size - max_size occasions to
    // scale down some tuples so the whole thing would fit into max_size. If
    // we are lucky, there will be no gaps at the end (or at least fewer gaps
    // than we would have if we always rounded down).
    bool dirty = true; // This flag prevents infinite loops if nothing can be made any smaller.
    while (dirty && (total_axis_size > max_size))
    {
        // This algorithm needs O(n*n) time. Let's hope that n is small enough.
        dirty = false;
        std::size_t current_index = 0;
        std::vector<double>* current_min = nullptr;

        for (std::size_t i = 0; i < n; ++i)
        {
            auto& d = scaling_data[i];
            if (!d[2])
            {
                // Ignore elements that cannot be made any smaller.
                continue;
            }
            if (!current_min || d[4] < (*current_min)[4])
            {
                // We are searching for the tuple where downscaling results
                // in the smallest relative volume error (compared to the
                // respective ideal volume).
                current_min = &d;
                current_index = i;
            }
        }

        for (std::size_t i = current_index; i < n; ++i)
        {
            // We must scale down ALL equal tuples. Otherwise, images that
            // are of equal size might appear to be of different size
            // afterwards. The downside of this approach is that it might
            // introduce more gaps than necessary.
            auto& d = scaling_data[i];
            if (!d[2] || d[1] != (*current_min)[1])
            {
                continue;
            }
            d[0] = d[3];
            d[2] = false; // only once per tuple
            total_axis_size -= 1;
            dirty = true;
        }
    }

    std::vector<double> result;
    for (const auto& d : scaling_data)
    {
        result.push_back(d[0]);
    }
    return result;
}

std::array<std::int32_t, 2>
ZoomModel::scale_image_size(const std::array<std::int32_t, 2>& size, const double scale) const noexcept
{
    return this->round_nonempty(this->scale(size, scale));
}

std::array<std::int32_t, 2>
ZoomModel::round_nonempty(const std::vector<double>& t) const noexcept
{
    std::array<std::int32_t, 2> result;
    for (std::size_t idx = 0; idx < t.size(); ++idx)
    {
        const auto x = static_cast<std::size_t>(std::round(t[idx]));
        result[idx] = (x > 0) ? x : 1;
    }
    return result;
}

std::vector<std::array<std::int32_t, 2>>
ZoomModel::fix_page_sizes(const std::vector<std::array<std::int32_t, 2>>& image_sizes,
                          const std::int32_t distribution_axis,
                          const std::vector<bool>& do_not_transform) const noexcept
{
    if (image_sizes.size() < 2)
    {
        return image_sizes;
    }

    // In double page mode, resize the smaller image to fit the bigger one

    // Transpose the sizes list: [(x1, x2, ...), (y1, y2, ...)]
    std::vector<std::vector<std::int32_t>> sizes(image_sizes[0].size(), std::vector<std::int32_t>(image_sizes.size()));
    for (std::size_t i = 0; i < image_sizes.size(); ++i)
    {
        for (std::size_t j = 0; j < image_sizes[0].size(); ++j)
        {
            sizes[j][i] = image_sizes[i][j];
        }
    }

    // Use axis else of distribution_axis
    std::vector<std::int32_t> axis_sizes = sizes[distribution_axis == 0 ? 1 : 0];
    //Max size of pages
    const auto max_size = *std::max_element(axis_sizes.cbegin(), axis_sizes.cend());

    // Scale ratio of every page if do transform
    std::vector<double> ratios(image_sizes.size(), 1.0f);
    for (std::size_t n = 0; n < axis_sizes.size(); ++n)
    {
        if (!do_not_transform[n])
        {
            ratios[n] = static_cast<double>(max_size) / axis_sizes[n];
        }
    }

    // Scale each page size according to the computed ratios
    std::vector<std::array<std::int32_t, 2>> scaled_sizes;
    for (std::size_t n = 0; n < image_sizes.size(); ++n)
    {
        std::array<std::int32_t, 2> scaled_page;
        scaled_page[0] = image_sizes[n][0] * ratios[n];
        scaled_page[1] = image_sizes[n][1] * ratios[n];
        scaled_sizes.push_back(scaled_page);
    }

    return scaled_sizes;
}

std::array<std::int32_t, 2>
ZoomModel::union_size(const std::vector<std::array<std::int32_t, 2>>& image_sizes,
                      const std::int32_t distribution_axis) const noexcept
{
    if (image_sizes.empty())
    {
        return {};
    }

    const auto n = image_sizes[0].size();
    std::array<std::int32_t, 2> union_size;

    for (std::size_t i = 0; i < n; ++i)
    {
        union_size[i] = std::accumulate(image_sizes.cbegin(),
                                        image_sizes.cend(),
                                        0,
                                        [i](const std::int32_t current_max, const std::array<std::int32_t, 2>& size)
                                        { return std::max<std::int32_t>(current_max, size[i]); });
    }

    union_size[distribution_axis] =
        std::accumulate(image_sizes.cbegin(),
                        image_sizes.cend(),
                        0,
                        [distribution_axis](const std::int32_t total, const std::array<std::int32_t, 2>& size)
                        { return total + size[distribution_axis]; });

    return union_size;
}

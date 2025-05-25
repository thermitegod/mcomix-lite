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

#include "enums.hpp"

class ZoomModel
{
  public:
    // ZoomModel(const std::shared_ptr<Settings>& settings);

    void set_fit_mode(ZoomModes fitmode) noexcept;
    void set_scale_up(const bool scale_up) noexcept;
    void set_user_zoom_log(const double zoom_log) noexcept;
    void zoom_in() noexcept;
    void zoom_out() noexcept;
    void reset_user_zoom() noexcept;

    [[nodiscard]] std::vector<double> scale(const std::array<std::int32_t, 2>& t, const double factor) const noexcept;

    [[nodiscard]] std::vector<std::array<std::int32_t, 2>>
    get_zoomed_size(const std::vector<std::array<std::int32_t, 2>>& image_sizes,
                    const std::array<std::int32_t, 2>& screen_size, const std::int32_t distribution_axis,
                    const std::vector<bool>& do_not_transform) const noexcept;

    /**
     * Returns scale that makes an image of size image_size respect the
     * limits imposed by limits. If no proper value can be determined,
     * this->identity_zoom is returned
     */
    [[nodiscard]] double preferred_scale(const std::array<std::int32_t, 2>& image_size,
                                         const std::vector<std::int32_t>& limits,
                                         const std::int32_t distribution_axis) const noexcept;

    /**
     * Returns a list or a tuple with the i-th element set to int x if
     * fitmode limits the size at the i-th axis to x, or -1 if fitmode has no
     * preference for this axis
     */
    [[nodiscard]] std::vector<std::int32_t> calc_limits(const std::array<std::int32_t, 2>& union_size,
                                                        const std::array<std::int32_t, 2>& screen_size,
                                                        ZoomModes fitmode, const bool allow_upscaling) const noexcept;

    /**
     * Calculates scales for a list of boxes that are distributed along a
     * given axis (without any gaps). If the resulting scales are applied to
     * their respective boxes, their new total size along axis will be as close
     * as possible to max_size. The current implementation ensures that equal
     * box sizes are mapped to equal scales.
     *
     * :param sizes: A list of box sizes.
     * :param axis: The axis along which those boxes are distributed.
     * :param max_size: The maximum size the scaled boxes may have along axis.
     * :param allow_upscaling: True if upscaling is allowed, False otherwise.
     * :param do_not_transform: True if the resulting scale must be 1, False otherwise.
     * :returns: A list of scales where the i-th scale belongs to the i-th box size.
     */
    [[nodiscard]] std::vector<double> scale_distributed(const std::vector<std::array<std::int32_t, 2>>& sizes,
                                                        const std::int32_t axis, const std::int32_t max_size,
                                                        const bool allow_upscaling,
                                                        const std::vector<bool>& do_not_transform) const noexcept;

    [[nodiscard]] std::array<std::int32_t, 2> scale_image_size(const std::array<std::int32_t, 2>& size,
                                                               double scale) const noexcept;

    /**
     * Rounds each element in the given vector. If the rounded value is less than or equal to 0,
     * sets it to 1 to ensure all dimensions are non-zero.
     */
    [[nodiscard]] std::array<std::int32_t, 2> round_nonempty(const std::vector<double>& t) const noexcept;

    /**
     * Adjusts the sizes of pages to fit the larger page in a double-page mode by scaling smaller pages.
     */
    [[nodiscard]] std::vector<std::array<std::int32_t, 2>>
    fix_page_sizes(const std::vector<std::array<std::int32_t, 2>>& image_sizes, const std::int32_t distribution_axis,
                   const std::vector<bool>& do_not_transform) const noexcept;

    /**
     * Computes the union size of all images along each axis.
     * The size along the distribution_axis is the sum of all image sizes in that axis.
     */
    [[nodiscard]] std::array<std::int32_t, 2> union_size(const std::vector<std::array<std::int32_t, 2>>& image_sizes,
                                                         const std::int32_t distribution_axis) const noexcept;

  private:
    double identity_zoom_ = 1.0;
    double identity_zoom_log_ = 0.0;
    double user_zoom_log_scale1_ = 4.0;
    std::int32_t min_user_zoom_log_ = -20;
    std::int32_t max_user_zoom_log_ = 12;

    // User zoom level
    double user_zoom_log_ = 0.0;

    // Image fit mode. Determines the base zoom level for an image by
    // calculating its maximum size.
    ZoomModes fitmode_ = ZoomModes::MANUAL;
    bool scale_up_ = false;

    // std::shared_ptr<Settings> settings;
};

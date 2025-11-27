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

#include <stop_token>

#include <glibmm.h>

#include <ztd/ztd.hxx>

#include "gui/lib/image-tools.hxx"
#include "gui/lib/thumbnailer.hxx"

void
gui::lib::thumbnailer::request(const request_data& request) noexcept
{
    {
        std::lock_guard<std::mutex> lock(this->mutex_);
        this->queue_.push(request);
    }
    this->cv_.notify_one();
}

void
gui::lib::thumbnailer::run(const std::stop_token& stoken) noexcept
{
    while (!stoken.stop_requested())
    {
        this->run_once(stoken);
    }
}

void
gui::lib::thumbnailer::run_once(const std::stop_token& stoken) noexcept
{
    request_data request;
    {
        std::unique_lock<std::mutex> lock(this->mutex_);
        this->cv_.wait(lock, stoken, [this] { return !queue_.empty(); });

        if (stoken.stop_requested())
        {
            return;
        }

        if (!this->queue_.empty())
        {
            request = this->queue_.front();
            this->queue_.pop();
        }
    }

    auto pixbuf = gui::lib::image_tools::create_thumbnail(request.file, request.thumb_size);

    if (!stoken.stop_requested())
    {
        this->signal_thumbnail_created().emit(request.page, pixbuf);
    }
}

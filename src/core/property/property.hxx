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

#include <concepts>
#include <utility>

#include <sigc++/sigc++.h>

// TODO
// - able to have Property<T> on a struct and emit on member change

// Similar to the Glib::Property<T> without needing to use GObject
// https://gnome.pages.gitlab.gnome.org/glibmm/classGlib_1_1Property.html

template<typename T> class Property
{
  public:
    using PropertyType = T;

    template<typename U> Property(U&& data) : value_(std::forward<U>(data)) {}

    operator const T&() const { return value_; }

    template<typename U>
    Property&
    operator=(U&& data) noexcept
        requires std::same_as<T, U> || std::convertible_to<U, T>
    {
        T converted_value = std::forward<U>(data);
        if (value_ != converted_value)
        {
            value_ = std::move(converted_value);
            signal_changed_.emit();
        }
        return *this;
    }

    template<typename U>
    friend bool
    operator==(const Property<T>& prop, const U& other) noexcept
        requires std::same_as<T, U> || std::convertible_to<U, T>
    {
        return prop.value_ == other;
    }

    const T&
    get() const noexcept
    {
        return value_;
    }

    sigc::signal<void()>&
    signal_changed() noexcept
    {
        return signal_changed_;
    }

  private:
    T value_;
    sigc::signal<void()> signal_changed_;
};

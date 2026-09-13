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

#include <utility>

#include <glaze/glaze.hpp>

#include "settings/property.hxx"

#include "bitflags/bitflags.hxx"

// property

namespace glz
{
template<typename T> struct from<JSON, Property<T>>
{
    static constexpr bool can_error = false;

    template<auto Opts>
    static void
    op(Property<T>& value, auto&&... args)
    {
        T raw{};
        parse<JSON>::template op<Opts>(raw, std::forward<decltype(args)>(args)...);
        value = Property<T>{raw};
    }
};

template<typename T> struct to<JSON, Property<T>>
{
    static constexpr bool can_error = false;

    template<auto Opts>
    static void
    op(const Property<T>& value, auto&&... args) noexcept
    {
        serialize<JSON>::template op<Opts>(value.get(), std::forward<decltype(args)>(args)...);
    }
};
} // namespace glz

// bit_flags

namespace glz
{
template<typename T>
    requires std::is_enum_v<T>
struct from<JSON, bit_flags<T>>
{
    static constexpr bool can_error = true;

    template<auto Opts>
    static void
    op(bit_flags<T>& value, auto&&... args)
    {
        using underlying_type = typename bit_flags<T>::underlying_type;
        underlying_type raw{};
        parse<JSON>::template op<Opts>(raw, std::forward<decltype(args)>(args)...);
        value = bit_flags<T>::create(raw);
    }
};

template<typename T>
    requires std::is_enum_v<T>
struct to<JSON, bit_flags<T>>
{
    static constexpr bool can_error = false;

    template<auto Opts>
    static void
    op(const bit_flags<T>& value, auto&&... args) noexcept
    {
        serialize<JSON>::template op<Opts>(value.data(), std::forward<decltype(args)>(args)...);
    }
};
} // namespace glz

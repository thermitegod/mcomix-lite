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
#include <initializer_list>
#include <type_traits>
#include <utility>

// Helper class for bitwise flag-like operations on scoped enums.
//
// This class provides a way to represent combinations of enum values without
// directly overloading operators on the enum type itself. This approach
// avoids ambiguity in the type system and allows the enum type to continue
// representing a single value, while the BitFlags can hold a combination
// of enum values.
//
// Example usage:
//
// enum class MyEnum { FlagA = 1 << 0, FlagB = 1 << 1, FlagC = 1 << 2 };
//
// BitFlags<MyEnum> flags = { MyEnum::FlagA, MyEnum::FlagC };
// flags.Unset(MyEnum::FlagA);
// if (flags.IsSet(MyEnum::FlagC)) {
//   // ...
// }
//
// flags |= MyEnum::FlagB;
// BitFlags<MyEnum> new_flags = ~flags;

// https://voithos.io/articles/type-safe-enum-class-bit-flags/

template<typename T>
    requires std::is_enum_v<T>
class bit_flags
{
  public:
    using underlying_type = std::underlying_type_t<T>;

    constexpr bit_flags() noexcept = default;

    constexpr explicit bit_flags(T v) noexcept : flags_{std::to_underlying(v)} {}

    constexpr bit_flags(std::initializer_list<T> vs) noexcept : bit_flags()
    {
        for (T v : vs)
        {
            flags_ |= std::to_underlying(v);
        }
    }

    static constexpr bit_flags
    create(underlying_type raw_flags) noexcept
    {
        return bit_flags(raw_flags);
    }

    template<typename... Args>
        requires(sizeof...(Args) > 0 && (std::same_as<T, Args> && ...))
    static constexpr bit_flags
    create(Args... args) noexcept
    {
        return bit_flags{args...};
    }

    [[nodiscard]] constexpr bool
    is_set(T v) const noexcept
    {
        return (flags_ & std::to_underlying(v)) == std::to_underlying(v);
    }

    constexpr void
    set(T v) noexcept
    {
        flags_ |= std::to_underlying(v);
    }

    constexpr void
    unset(T v) noexcept
    {
        flags_ &= ~std::to_underlying(v);
    }

    constexpr void
    clear() noexcept
    {
        flags_ = 0;
    }

    [[nodiscard]] constexpr explicit
    operator bool() const noexcept
    {
        return flags_ != 0;
    }

    [[nodiscard]] constexpr T
    unwrap() const noexcept
    {
        return static_cast<T>(flags_);
    }

    [[nodiscard]] constexpr underlying_type
    data() const noexcept
    {
        return flags_;
    }

    friend constexpr bit_flags
    operator|(bit_flags lhs, T rhs) noexcept
    {
        return bit_flags(lhs.flags_ | std::to_underlying(rhs));
    }

    friend constexpr bit_flags
    operator|(bit_flags lhs, bit_flags rhs) noexcept
    {
        return bit_flags(lhs.flags_ | rhs.flags_);
    }

    friend constexpr bit_flags
    operator&(bit_flags lhs, T rhs) noexcept
    {
        return bit_flags(lhs.flags_ & std::to_underlying(rhs));
    }

    friend constexpr bit_flags
    operator&(bit_flags lhs, bit_flags rhs) noexcept
    {
        return bit_flags(lhs.flags_ & rhs.flags_);
    }

    friend constexpr bit_flags
    operator^(bit_flags lhs, T rhs) noexcept
    {
        return bit_flags(lhs.flags_ ^ std::to_underlying(rhs));
    }

    friend constexpr bit_flags
    operator^(bit_flags lhs, bit_flags rhs) noexcept
    {
        return bit_flags(lhs.flags_ ^ rhs.flags_);
    }

    friend constexpr bit_flags&
    operator|=(bit_flags& lhs, T rhs) noexcept
    {
        lhs.flags_ |= std::to_underlying(rhs);
        return lhs;
    }

    friend constexpr bit_flags&
    operator|=(bit_flags& lhs, bit_flags rhs) noexcept
    {
        lhs.flags_ |= rhs.flags_;
        return lhs;
    }

    friend constexpr bit_flags&
    operator&=(bit_flags& lhs, T rhs) noexcept
    {
        lhs.flags_ &= std::to_underlying(rhs);
        return lhs;
    }

    friend constexpr bit_flags&
    operator&=(bit_flags& lhs, bit_flags rhs) noexcept
    {
        lhs.flags_ &= rhs.flags_;
        return lhs;
    }

    friend constexpr bit_flags&
    operator^=(bit_flags& lhs, T rhs) noexcept
    {
        lhs.flags_ ^= std::to_underlying(rhs);
        return lhs;
    }

    friend constexpr bit_flags&
    operator^=(bit_flags& lhs, bit_flags rhs) noexcept
    {
        lhs.flags_ ^= rhs.flags_;
        return lhs;
    }

    friend constexpr bit_flags
    operator~(const bit_flags& bf) noexcept
    {
        return bit_flags(~bf.flags_);
    }

    friend constexpr bool operator==(const bit_flags&, const bit_flags&) = default;

  private:
    constexpr explicit bit_flags(underlying_type flags) noexcept : flags_(flags) {}

    underlying_type flags_{0};
};

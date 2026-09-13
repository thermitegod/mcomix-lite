/**
 * Copyright (C) 2026 Brandon Zorn <brandonzorn@cock.li>
 *
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

#include <cstdint>

#include <doctest/doctest.h>

#include "settings/extra/glaze.hxx"

#include "bitflags/bitflags.hxx"

enum class b_flags_1 : std::uint32_t
{
    flag1 = 1 << 0,
    flag2 = 1 << 1,
    flag3 = 1 << 2,
};

enum class b_flags_2 : std::int32_t
{
    flag1 = 1 << 0,
    flag2 = 1 << 1,
    flag3 = 1 << 2,
};

TEST_SUITE("bit_flags tests" * doctest::description(""))
{
    TEST_CASE_TEMPLATE("bit_flags", T, b_flags_1, b_flags_2)
    {
        using flags_t = bit_flags<T>;

        SUBCASE("constructor")
        {
            {
                flags_t f1{};
                CHECK_FALSE(static_cast<bool>(f1));
                CHECK(f1.data() == 0);
            }

            {
                flags_t f1{T::flag1};
                CHECK(static_cast<bool>(f1));
                CHECK(f1.is_set(T::flag1));
                CHECK_FALSE(f1.is_set(T::flag2));
            }

            {
                flags_t f1{T::flag1, T::flag3};
                CHECK(f1.is_set(T::flag1));
                CHECK_FALSE(f1.is_set(T::flag2));
                CHECK(f1.is_set(T::flag3));
            }
        }

        SUBCASE("create")
        {
            auto f1 = flags_t::create(T::flag1, T::flag2);
            CHECK(f1.is_set(T::flag1));
            CHECK(f1.is_set(T::flag2));
            CHECK_FALSE(f1.is_set(T::flag3));

            auto f2 = flags_t::create(std::to_underlying(T::flag2) | std::to_underlying(T::flag3));
            CHECK_FALSE(f2.is_set(T::flag1));
            CHECK(f2.is_set(T::flag2));
            CHECK(f2.is_set(T::flag3));
        }

        SUBCASE("set, unset, clear")
        {
            flags_t f1{};

            f1.set(T::flag1);
            CHECK(f1.is_set(T::flag1));

            f1.set(T::flag2);
            CHECK(f1.is_set(T::flag1));
            CHECK(f1.is_set(T::flag2));

            f1.unset(T::flag1);
            CHECK_FALSE(f1.is_set(T::flag1));
            CHECK(f1.is_set(T::flag2));

            f1.clear();
            CHECK_FALSE(static_cast<bool>(f1));
            CHECK(f1.data() == 0);
        }

        SUBCASE("operators")
        {
            flags_t f1{T::flag1};
            flags_t f2{T::flag2};

            // OR
            auto r1 = f1 | f2;
            CHECK(r1.is_set(T::flag1));
            CHECK(r1.is_set(T::flag2));

            auto r2 = f1 | T::flag3;
            CHECK(r2.is_set(T::flag1));
            CHECK(r2.is_set(T::flag3));

            // AND
            auto r3 = r1 & f1;
            CHECK(r3.is_set(T::flag1));
            CHECK_FALSE(r3.is_set(T::flag2));

            // XOR
            auto r4 = r1 ^ f1;
            CHECK_FALSE(r4.is_set(T::flag1));
            CHECK(r4.is_set(T::flag2));
        }

        SUBCASE("compound assignment operators")
        {
            flags_t f1{T::flag1};

            // OR
            f1 |= T::flag2;
            CHECK(f1.is_set(T::flag1));
            CHECK(f1.is_set(T::flag2));

            // AND
            f1 &= T::flag1;
            CHECK(f1.is_set(T::flag1));
            CHECK_FALSE(f1.is_set(T::flag2));

            // XOR
            f1 ^= T::flag1;
            CHECK_FALSE(f1.is_set(T::flag1));
        }

        SUBCASE("comparison operators")
        {
            flags_t f1{T::flag1, T::flag2};
            flags_t f2{T::flag1, T::flag2};
            flags_t f3{T::flag3};

            CHECK(f1 == f2);
            CHECK(f1 != f3);

            flags_t invert = ~f1;
            CHECK_FALSE(invert.is_set(T::flag1));
            CHECK_FALSE(invert.is_set(T::flag2));
            CHECK(invert.is_set(T::flag3));
        }

        SUBCASE("switch compile test")
        {
            flags_t f1{T::flag1, T::flag3};

            switch (f1.unwrap())
            {
                case T::flag1:
                    break;
                case T::flag2:
                    break;
                case T::flag3:
                    break;
            }
        }

        SUBCASE("glaze")
        {
            auto original = flags_t::create(T::flag1, T::flag3);

            std::string buffer{};
            auto write_ctx = glz::write_json(original, buffer);
            CHECK_FALSE(write_ctx);

            flags_t parsed{};
            auto read_ctx = glz::read_json(parsed, buffer);
            CHECK_FALSE(read_ctx);

            CHECK(parsed == original);
            CHECK(parsed.is_set(T::flag1));
            CHECK_FALSE(parsed.is_set(T::flag2));
            CHECK(parsed.is_set(T::flag3));
        }
    }
}

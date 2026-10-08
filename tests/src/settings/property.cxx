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

#include "property/property.hxx"

enum class property_enum_test
{
    a,
    b,
};

struct property_struct_test
{
    std::int32_t x = 0;
    std::int32_t y = 0;

    bool operator==(const property_struct_test& other) const = default;
};

TEST_SUITE("Property<T>")
{
    TEST_CASE("bool")
    {
        Property<bool> prop = true;

        REQUIRE(prop);

        SUBCASE("assignment")
        {
            bool value = prop;
            CHECK(value);

            prop = false;
            CHECK_FALSE(prop);
        }

        SUBCASE("signals")
        {
            std::uint32_t emit_counter = 0;

            prop.signal_changed().connect([&emit_counter]() { emit_counter++; });

            prop = false;
            CHECK(emit_counter == 1);

            SUBCASE("same value")
            {
                prop = false;
                CHECK(emit_counter == 1);
            }

            SUBCASE("different value")
            {
                prop = true;
                CHECK(emit_counter == 2);
            }
        }
    }

    TEST_CASE("std::int32_t")
    {
        Property<std::int32_t> prop = 50;

        REQUIRE(prop == 50);

        SUBCASE("assignment")
        {
            std::int32_t value = prop;
            CHECK(value == 50);

            prop = 100;
            CHECK(prop == 100);
        }

        SUBCASE("signals")
        {
            std::uint32_t emit_counter = 0;

            prop.signal_changed().connect([&emit_counter]() { emit_counter++; });

            prop = 100;
            CHECK(emit_counter == 1);

            SUBCASE("same value")
            {
                prop = 100;
                CHECK(emit_counter == 1);
            }

            SUBCASE("different value")
            {
                prop = 200;
                CHECK(emit_counter == 2);
            }
        }
    }

    TEST_CASE("std::uint32_t")
    {
        Property<std::uint32_t> prop = 50u;

        REQUIRE(prop == 50u);

        SUBCASE("assignment")
        {
            std::uint32_t value = prop;
            CHECK(value == 50u);

            prop = 100u;
            CHECK(prop == 100u);
        }

        SUBCASE("signals")
        {
            std::uint32_t emit_counter = 0;

            prop.signal_changed().connect([&emit_counter]() { emit_counter++; });

            prop = 100u;
            CHECK(emit_counter == 1);

            SUBCASE("same value")
            {
                prop = 100u;
                CHECK(emit_counter == 1);
            }

            SUBCASE("different value")
            {
                prop = 200u;
                CHECK(emit_counter == 2);
            }
        }
    }

    TEST_CASE("std::string")
    {
        Property<std::string> prop = "string";

        REQUIRE(prop == "string");

        SUBCASE("assignment")
        {
            std::string value = prop;
            CHECK(value == "string");

            prop = "test string";
            CHECK(prop == "test string");
        }

        SUBCASE("signals")
        {
            std::uint32_t emit_counter = 0;

            prop.signal_changed().connect([&emit_counter]() { emit_counter++; });

            prop = "test string";
            CHECK(emit_counter == 1);

            SUBCASE("same value")
            {
                prop = "test string";
                CHECK(emit_counter == 1);
            }

            SUBCASE("different value")
            {
                prop = "string";
                CHECK(emit_counter == 2);
            }
        }
    }

    TEST_CASE("property_enum_test")
    {
        Property<property_enum_test> prop = property_enum_test::a;

        REQUIRE(prop == property_enum_test::a);

        SUBCASE("assignment")
        {
            CHECK(prop == property_enum_test::a);

            property_enum_test value = prop;
            CHECK(value == property_enum_test::a);

            prop = property_enum_test::b;
            CHECK(prop == property_enum_test::b);
        }

        SUBCASE("signals")
        {
            std::uint32_t emit_counter = 0;

            prop.signal_changed().connect([&emit_counter]() { emit_counter++; });

            prop = property_enum_test::b;
            CHECK(emit_counter == 1);

            SUBCASE("same value")
            {
                prop = property_enum_test::b;
                CHECK(emit_counter == 1);
            }

            SUBCASE("different value")
            {
                prop = property_enum_test::a;
                CHECK(emit_counter == 2);
            }
        }
    }

    TEST_CASE("property_struct_test")
    {
        Property<property_struct_test> prop = property_struct_test{10, 20};

        REQUIRE(prop == property_struct_test{10, 20});

        SUBCASE("assignment")
        {
            property_struct_test value = prop;
            CHECK(value == property_struct_test{10, 20});

            prop = property_struct_test{100, 200};
            CHECK(prop == property_struct_test{100, 200});
        }

        SUBCASE("signals")
        {
            std::uint32_t emit_counter = 0;

            prop.signal_changed().connect([&emit_counter]() { emit_counter++; });

            prop = property_struct_test{100, 200};
            CHECK(emit_counter == 1);

            SUBCASE("same value")
            {
                prop = property_struct_test{100, 200};
                CHECK(emit_counter == 1);
            }

            SUBCASE("different value")
            {
                prop = property_struct_test{10, 20};
                CHECK(emit_counter == 2);
            }
        }
    }
}

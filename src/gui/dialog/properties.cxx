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
#include <chrono>
#include <filesystem>
#include <memory>

#include <glibmm.h>
#include <gtkmm.h>
#include <sigc++/sigc++.h>

#include <ztd/ztd.hxx>

#include "gui/dialog/properties.hxx"

#include "vfs/file-handler.hxx"

#include "vfs/utils/utils.hxx"

class PropertiesPage : public Gtk::Box
{
  public:
    explicit PropertiesPage() noexcept
    {
        set_orientation(Gtk::Orientation::VERTICAL);
        set_margin(6);
        set_homogeneous(false);
        set_vexpand(true);

        image_box_.set_orientation(Gtk::Orientation::HORIZONTAL);
        image_box_.set_margin(5);
        image_.set_content_fit(Gtk::ContentFit::CONTAIN);
        image_.set_hexpand(false);
        image_.set_vexpand(false);
        image_.set_halign(Gtk::Align::CENTER);
        image_.set_valign(Gtk::Align::CENTER);
        image_box_.append(image_);
        border_frame_.set_size_request(-1, 130);
        border_frame_.set_child(image_info_box_);
        image_info_box_.set_orientation(Gtk::Orientation::VERTICAL);
        image_info_box_.set_margin(5);
        image_info_box_.set_spacing(0);
        image_box_.append(border_frame_);
        append(image_box_);

        info_box_.set_orientation(Gtk::Orientation::HORIZONTAL);
        info_box_.set_margin(5);
        append(info_box_);
    }

    void
    set_filename(const std::filesystem::path& filename) noexcept
    {
        auto label = Gtk::make_managed<Gtk::Label>();
        label->set_markup(std::format("<b>{}</b>", filename.string()));
        label->set_xalign(0.0);
        label->set_yalign(0.5);
        label->set_selectable(true);
        label->set_wrap(true);
        image_info_box_.append(*label);

        auto box = Gtk::make_managed<Gtk::Box>();
        box->set_hexpand(true);
        box->set_vexpand(true);
        image_info_box_.append(*box);
    }

    void
    set_main_info(std::vector<std::string> info) noexcept
    {
        for (const auto& text : info)
        {
            auto label = Gtk::make_managed<Gtk::Label>();
            label->set_text(text);
            label->set_xalign(0.0);
            label->set_yalign(0.5);
            image_info_box_.append(*label);
        }
    }

    void
    set_secondary_info(const std::vector<std::array<std::string, 2>>& info) noexcept
    {
        auto lbox = Gtk::make_managed<Gtk::Box>();
        lbox->set_orientation(Gtk::Orientation::VERTICAL);
        lbox->set_homogeneous(true);
        lbox->set_spacing(8);
        lbox->set_margin_end(10);

        auto rbox = Gtk::make_managed<Gtk::Box>();
        rbox->set_orientation(Gtk::Orientation::VERTICAL);
        rbox->set_homogeneous(true);
        rbox->set_spacing(8);

        info_box_.append(*lbox);
        info_box_.append(*rbox);

        for (const auto& [desc, value] : info)
        {
            {
                auto label = Gtk::make_managed<Gtk::Label>();
                label->set_markup(std::format("<b>{}:</b>", desc));
                label->set_xalign(1.0);
                label->set_yalign(1.0);
                lbox->append(*label);
            }

            {
                auto label = Gtk::make_managed<Gtk::Label>();
                label->set_text(value);
                label->set_xalign(0.0);
                label->set_yalign(1.0);
                label->set_selectable(true);
                rbox->append(*label);
            }
        }
    }

    void
    set_thumbnail(const Glib::RefPtr<Gdk::Paintable>& paintable) noexcept
    {
        image_.set_paintable(paintable);
    }

  private:
    Gtk::Picture image_;
    Gtk::Frame border_frame_;
    Gtk::Box image_info_box_;
    Gtk::Box image_box_;

    Gtk::Box info_box_;

    std::shared_ptr<vfs::file_handler> file_handler_;
};

gui::dialog::properties::properties(Gtk::ApplicationWindow& parent,
                                    const std::shared_ptr<vfs::file_handler>& file_handler,
                                    const std::shared_ptr<gui::lib::view_state>& view_state,
                                    const std::shared_ptr<config::settings>& settings) noexcept
    : file_handler_(file_handler), view_state_(view_state), settings_(settings)
{
    set_transient_for(parent);
    set_modal(true);

    set_size_request(470, 400);
    set_title("Preferences");
    set_resizable(false);

    box_ = Gtk::Box(Gtk::Orientation::VERTICAL, 5);
    box_.set_margin(5);

    box_.append(notebook_);

    if (file_handler_->is_archive())
    {
        init_archive_tab();
    }

    if (view_state_->is_displaying_double())
    {
        const auto p = file_handler_->image_handler()->get_current_page();

        if (view_state_->is_manga_mode())
        {
            init_image_tab(p + 1, "Left Image");
            init_image_tab(p, "Right Image");
        }
        else
        {
            init_image_tab(p, "Left Image");
            init_image_tab(p + 1, "Right Image");
        }
    }
    else
    {
        const auto p = file_handler_->image_handler()->get_current_page();

        init_image_tab(p, "Image");
    }

    auto key_controller = Gtk::EventControllerKey::create();
    key_controller->signal_key_pressed().connect(sigc::mem_fun(*this, &properties::on_key_press),
                                                 false);
    add_controller(key_controller);

    button_box_ = Gtk::Box(Gtk::Orientation::HORIZONTAL, 5);
    button_close_ = Gtk::Button("Close", true);
    button_close_.signal_clicked().connect([this]() { on_button_close_clicked(); });
    button_box_.set_halign(Gtk::Align::END);
    button_box_.append(button_close_);
    box_.append(button_box_);

    set_child(box_);

    set_visible(true);
}

bool
gui::dialog::properties::on_key_press(std::uint32_t keyval, std::uint32_t keycode,
                                      Gdk::ModifierType state) noexcept
{
    (void)keycode;
    (void)state;
    if (keyval == GDK_KEY_Escape)
    {
        on_button_close_clicked();
    }
    return false;
}

void
gui::dialog::properties::on_button_close_clicked() noexcept
{
    close();
}

std::vector<std::array<std::string, 2>>
gui::dialog::properties::secondary_info(const std::filesystem::path& path) noexcept
{
    const auto stat = ztd::statx::create(path);
    if (!stat)
    {
        return {};
    }

    return {
        {"Location", path.parent_path()},
        {"Size", std::format("{}", vfs::utils::file_size(stat->size(), settings_->si_units))},
        {"Accessed", std::format("{}", std::chrono::floor<std::chrono::seconds>(stat->atime()))},
        {"Created", std::format("{}", std::chrono::floor<std::chrono::seconds>(stat->btime()))},
        {"Metadata", std::format("{}", std::chrono::floor<std::chrono::seconds>(stat->ctime()))},
        {"Modified", std::format("{}", std::chrono::floor<std::chrono::seconds>(stat->mtime()))},
        {"Permissions", std::format("{}", stat->perms_fancy())},
        {"Owner", std::format("{}", ztd::passwd::create(stat->uid().data())->name())},
        {"Group", std::format("{}", ztd::group::create(stat->gid().data())->name())},
    };
}

void
gui::dialog::properties::init_archive_tab() noexcept
{
    auto page = PropertiesPage();

    page.set_filename(file_handler_->get_real_path().filename());

    auto thumb = file_handler_->image_handler()->get_thumbnail(1, 256);
    page.set_thumbnail(thumb);

    page.set_main_info(
        {std::format("{} pages", file_handler_->image_handler()->get_number_of_pages()),
         file_handler_->is_archive() ? "Archive File" : "Image File"});

    page.set_secondary_info(secondary_info(file_handler_->get_real_path()));

    auto tab_label = Gtk::Label("Archive");
    notebook_.append_page(page, tab_label);
}

void
gui::dialog::properties::init_image_tab(const page_t p, std::string_view label) noexcept
{
    auto page = PropertiesPage();

    const auto path = file_handler_->image_handler()->get_path_to_page(p);

    page.set_filename(path.filename());

    auto thumb = file_handler_->image_handler()->get_thumbnail(p, 256);
    page.set_thumbnail(thumb);

    const auto [width, height] = file_handler_->image_handler()->get_page_size(p);

    page.set_main_info(
        {std::format("{}x{}", width, height), file_handler_->image_handler()->get_mime_name(p)});

    page.set_secondary_info(secondary_info(path));

    auto tab_label = Gtk::Label(label.data());
    notebook_.append_page(page, tab_label);
}

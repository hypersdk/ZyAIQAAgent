mod paths;
mod server;

use paths::AppSettings;
use server::ServerState;
use tauri::{Manager, RunEvent, WindowEvent};

#[tauri::command]
fn dashboard_url(state: tauri::State<ServerState>) -> Result<Option<String>, String> {
    server::dashboard_url(&state)
}

#[tauri::command]
fn get_settings() -> AppSettings {
    paths::load_settings()
}

#[tauri::command]
fn set_settings(settings: AppSettings) -> Result<(), String> {
    paths::save_settings(&settings)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let app = tauri::Builder::default()
        .manage(ServerState::default())
        .invoke_handler(tauri::generate_handler![
            dashboard_url,
            get_settings,
            set_settings,
        ])
        .setup(|app| {
            let settings = paths::load_settings();
            server::start_in_background(app.handle().clone(), settings.zyvor_qa_bin);
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building the Zyvor QA Agent desktop app");

    // Killing the spawned `zyvor-qa serve` child needs to survive every way
    // this single-window app can end, not just one of them — verified live
    // that only handling the window's own CloseRequested event (via
    // `on_window_event`) misses Cmd+Q / Dock "Quit" / the app-menu Quit
    // item, which macOS delivers as an app-level RunEvent::ExitRequested
    // instead, leaving the server orphaned with its port still bound.
    app.run(|app_handle, event| match event {
        RunEvent::WindowEvent {
            event: WindowEvent::CloseRequested { .. },
            ..
        } => {
            // This is a single-window utility app — there's no reason to
            // keep `zyvor-qa serve` running invisibly after its only window
            // closes, so treat "close the window" as "quit the app" rather
            // than leaving it lingering in the Dock with nothing to show.
            server::shutdown(&app_handle.state::<ServerState>());
            app_handle.exit(0);
        }
        RunEvent::ExitRequested { .. } | RunEvent::Exit => {
            server::shutdown(&app_handle.state::<ServerState>());
        }
        _ => {}
    });
}

mod paths;
mod server;

use paths::AppSettings;
use server::ServerState;
use tauri::{Manager, WindowEvent};

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
    tauri::Builder::default()
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
        .on_window_event(|window, event| {
            // Kill the spawned `zyvor-qa serve` child when the (only) window
            // closes — otherwise it's an orphaned process silently holding a
            // port after the app appears to have quit.
            if matches!(event, WindowEvent::CloseRequested { .. } | WindowEvent::Destroyed) {
                let state = window.state::<ServerState>();
                server::shutdown(&state);
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running the Zyvor QA Agent desktop app");
}

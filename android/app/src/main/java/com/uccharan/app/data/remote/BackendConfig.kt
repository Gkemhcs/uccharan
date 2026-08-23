package com.uccharan.app.data.remote

import com.uccharan.app.BuildConfig

/**
 * Single source of truth for the backend URL. Debug builds default to the
 * emulator's route to the host machine's localhost (10.0.2.2) so local
 * `uvicorn` runs are reachable without any config; the real Render URL gets
 * set once here after deploy and release builds use it automatically.
 */
object BackendConfig {
    val baseUrl: String = BuildConfig.BACKEND_BASE_URL
}

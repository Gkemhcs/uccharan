plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.google.services)
}

android {
    namespace = "com.uccharan.app"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "com.uccharan.app"
        minSdk = 26
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        // TEMPORARY: cloudflared quick tunnel to local dev backend, while Render
        // deploy is being sorted out. This URL changes every time the tunnel is
        // restarted (see backend/README.md) — replace with the real Render URL
        // once that's deployed, and physical-device testing should use whichever
        // of these is actually reachable (10.0.2.2 only works on the emulator).
        buildConfigField("String", "BACKEND_BASE_URL", "\"https://pound-gain-defeat-minneapolis.trycloudflare.com\"")

        // Web-application OAuth client ID from google-services.json (oauth_client
        // type 3) — required by Credential Manager's GetGoogleIdOption. Not a
        // secret (it's a public identifier, safe to commit), unlike the JSON file.
        buildConfigField(
            "String",
            "GOOGLE_WEB_CLIENT_ID",
            "\"362298747158-6eov8as57pdr438ko7jo46n3hq6kocla.apps.googleusercontent.com\"",
        )
    }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
}

dependencies {
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.material.icons.extended)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)

    // Firebase (Auth + Firestore) — versions come from the BoM, don't pin them individually
    implementation(platform(libs.firebase.bom))
    implementation(libs.firebase.auth)
    implementation(libs.firebase.firestore)

    // Google Sign-In via Credential Manager (current, non-deprecated approach)
    implementation(libs.androidx.credentials)
    implementation(libs.androidx.credentials.play.services.auth)
    implementation(libs.googleid)

    // Navigation + ViewModel/state in Compose
    implementation(libs.androidx.navigation.compose)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.lifecycle.runtime.compose)

    // Coroutines (+ .await() bridge for Firebase's Task-based APIs)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.kotlinx.coroutines.play.services)

    // Backend HTTP calls — no codegen, deliberately simple for this app's size
    implementation(libs.okhttp)

    testImplementation(libs.junit)
    testImplementation(libs.mockk)
    testImplementation(libs.kotlinx.coroutines.test)
    testImplementation(libs.okhttp.mockwebserver)
    // Real org.json implementation for unit tests — android.jar's version on the
    // plain JVM test classpath is a stub that throws on every method call.
    testImplementation(libs.org.json)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.compose.ui.test.junit4)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.junit)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
    debugImplementation(libs.androidx.compose.ui.tooling)
}
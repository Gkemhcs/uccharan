package com.uccharan.app

import android.app.Application
import com.google.firebase.crashlytics.FirebaseCrashlytics
import com.uccharan.app.di.AppContainer

class UccharanApplication : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer()
        // Once this is on a learner's phone, a crash there is otherwise
        // invisible — this is the only way to find out it happened, let
        // alone why. Off in debug builds so local dev testing doesn't
        // pollute the dashboard with builds that were never actually shipped.
        FirebaseCrashlytics.getInstance().isCrashlyticsCollectionEnabled = !BuildConfig.DEBUG
    }
}

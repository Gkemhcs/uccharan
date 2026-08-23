package com.uccharan.app

import android.app.Application
import com.uccharan.app.di.AppContainer

class UccharanApplication : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer()
    }
}

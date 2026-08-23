package com.uccharan.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.Modifier
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.ui.navigation.UccharanNavHost
import com.uccharan.app.ui.theme.UccharanTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val container = (application as UccharanApplication).container

        setContent {
            CompositionLocalProvider(LocalAppContainer provides container) {
                UccharanTheme {
                    Surface(modifier = Modifier.fillMaxSize()) {
                        UccharanNavHost()
                    }
                }
            }
        }
    }
}

package com.uccharan.app.di

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.runtime.Composable

/**
 * Thin bridge between manual DI (AppContainer) and Compose's `viewModel()`.
 * Avoids every screen needing its own ViewModelProvider.Factory boilerplate.
 */
@Composable
inline fun <reified VM : ViewModel> uccharanViewModel(crossinline create: (AppContainer) -> VM): VM {
    val container = LocalAppContainer.current
    return viewModel(factory = viewModelFactory { create(container) })
}

inline fun <VM : ViewModel> viewModelFactory(crossinline create: () -> VM): androidx.lifecycle.ViewModelProvider.Factory =
    object : androidx.lifecycle.ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T = create() as T
    }

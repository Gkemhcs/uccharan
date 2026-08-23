package com.uccharan.app

import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.TestDispatcher
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import org.junit.rules.TestWatcher
import org.junit.runner.Description

/**
 * viewModelScope resolves to Dispatchers.Main, which doesn't exist on the JVM
 * unit-test runtime by default. This swaps in a test dispatcher for the
 * duration of each test.
 *
 * Deliberately UnconfinedTestDispatcher, not StandardTestDispatcher: our
 * ViewModels launch a coroutine in `init {}` and tests then read
 * `uiState.value` synchronously right after construction. Unconfined runs
 * coroutines eagerly up to their first suspension point, so that state is
 * already updated by the time the assertion runs — Standard would leave it
 * queued until an explicit advanceUntilIdle(), failing every such test.
 */
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher(),
) : TestWatcher() {
    override fun starting(description: Description) {
        kotlinx.coroutines.Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        kotlinx.coroutines.Dispatchers.resetMain()
    }
}

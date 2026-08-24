package com.uccharan.app.ui.signin

import android.app.Activity
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.google.firebase.FirebaseException
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.PhoneAuthCredential
import com.google.firebase.auth.PhoneAuthOptions
import com.google.firebase.auth.PhoneAuthProvider
import com.uccharan.app.data.repository.friendlyAuthErrorMessage
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import java.util.concurrent.TimeUnit

@Composable
fun PhoneSignInScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel { PhoneSignInViewModel(container.authRepository) }
    val uiState by viewModel.uiState.collectAsState()

    Column(modifier = Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.Center) {
        Text("Sign in with phone", style = MaterialTheme.typography.headlineSmall)
        Spacer(modifier = Modifier.height(24.dp))

        when (uiState.step) {
            PhoneSignInStep.ENTER_PHONE -> {
                OutlinedTextField(
                    value = uiState.phoneNumber,
                    onValueChange = viewModel::onPhoneNumberChange,
                    label = { Text("Phone number") },
                    placeholder = { Text("+91XXXXXXXXXX") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                    modifier = Modifier.fillMaxWidth(),
                )
                Text(
                    "Include your country code (e.g. +91 for India).",
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 4.dp),
                )
            }
            PhoneSignInStep.ENTER_OTP -> {
                OutlinedTextField(
                    value = uiState.otpCode,
                    onValueChange = viewModel::onOtpChange,
                    label = { Text("6-digit code") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
                    modifier = Modifier.fillMaxWidth(),
                )
                Text(
                    "We sent a code to ${uiState.phoneNumber}.",
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 4.dp),
                )
            }
        }

        uiState.errorMessage?.let { message ->
            Text(
                text = message,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 8.dp),
            )
        }

        Spacer(modifier = Modifier.height(20.dp))

        if (uiState.isLoading) {
            CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
        } else {
            when (uiState.step) {
                PhoneSignInStep.ENTER_PHONE -> Button(
                    onClick = { startPhoneVerification(context, uiState.phoneNumber, viewModel) },
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("Send code") }
                PhoneSignInStep.ENTER_OTP -> Button(
                    onClick = viewModel::onSubmitOtp,
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("Verify") }
            }
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(onClick = onBack, modifier = Modifier.fillMaxWidth()) { Text("Back") }
        }
    }
}

/**
 * Firebase's PhoneAuthProvider needs an Activity (for reCAPTCHA/Play Integrity
 * fallback UI), so this runs from the UI layer rather than the ViewModel —
 * see the class doc on PhoneSignInViewModel.
 */
private fun startPhoneVerification(context: android.content.Context, phoneNumber: String, viewModel: PhoneSignInViewModel) {
    val activity = context as? Activity ?: return
    viewModel.onVerificationStarted()

    val options = PhoneAuthOptions.newBuilder(FirebaseAuth.getInstance())
        .setPhoneNumber(phoneNumber)
        .setTimeout(60L, TimeUnit.SECONDS)
        .setActivity(activity)
        .setCallbacks(object : PhoneAuthProvider.OnVerificationStateChangedCallbacks() {
            override fun onVerificationCompleted(credential: PhoneAuthCredential) {
                viewModel.onAutoVerificationCompleted(credential)
            }

            override fun onVerificationFailed(exception: FirebaseException) {
                viewModel.onVerificationFailed(friendlyAuthErrorMessage(exception))
            }

            override fun onCodeSent(verificationId: String, token: PhoneAuthProvider.ForceResendingToken) {
                viewModel.onCodeSent(verificationId)
            }
        })
        .build()

    PhoneAuthProvider.verifyPhoneNumber(options)
}

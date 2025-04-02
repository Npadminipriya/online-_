let generatedOTP = null;

function sendOTP() {
    const email = document.getElementById("email").value;

    if (!email.includes("@") || !email.includes(".")) {
        document.getElementById("message").innerHTML = "❌ Enter a valid email!";
        return;
    }

    // Generate a 6-digit OTP
    generatedOTP = Math.floor(100000 + Math.random() * 900000);
    console.log("Generated OTP:", generatedOTP); // Simulating email sending

    // Show OTP input field
    document.getElementById("otp-section").style.display = "block";
    document.getElementById("message").innerHTML = "✅ OTP sent to " + email;
}

function verifyOTP() {
    const enteredOTP = document.getElementById("otp").value;

    if (enteredOTP == generatedOTP) {
        document.getElementById("message").innerHTML = "✅ Email Verified Successfully!";
        document.getElementById("message").style.color = "green";
    } else {
        document.getElementById("message").innerHTML = "❌ Incorrect OTP, try again.";
        document.getElementById("message").style.color = "red";
    }
}
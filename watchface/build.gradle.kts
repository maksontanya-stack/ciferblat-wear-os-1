plugins { id("com.android.application") }
android {
    namespace = "ru.meta.wearos.classic1"
    compileSdk = 35
    defaultConfig {
        applicationId = "ru.meta.wearos.classic1"
        minSdk = 33
        targetSdk = 33
        versionCode = 2
        versionName = "1.1.0-preview"
    }
    buildTypes {
        debug {
            isMinifyEnabled = true
            isShrinkResources = false
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = false
        }
    }
}

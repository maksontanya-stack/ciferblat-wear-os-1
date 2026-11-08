plugins { id("com.android.application") }
android {
    namespace = "ru.meta.wearos.classic1"
    compileSdk = 35
    defaultConfig {
        applicationId = "ru.meta.wearos.classic1"
        minSdk = 33
        targetSdk = 33
        versionCode = 1
        versionName = "1.0.0"
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

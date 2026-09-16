# Proguard rules for YourBrowser Android
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
-keepattributes JavascriptInterface
-keep public class com.yourbrowser.app.** { *; }

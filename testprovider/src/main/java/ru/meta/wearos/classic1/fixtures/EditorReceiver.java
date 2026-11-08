package ru.meta.wearos.classic1.fixtures;
import android.content.*;
public class EditorReceiver extends BroadcastReceiver {
 @Override public void onReceive(Context context,Intent intent){
  if("weather_swapped".equals(intent.getStringExtra("command"))){
   context.getSharedPreferences("fixture",0).edit().putBoolean("weather_swapped",intent.getBooleanExtra("enabled",false)).commit();
   androidx.wear.watchface.complications.datasource.ComplicationDataSourceUpdateRequester.create(context,new ComponentName(context,FixtureService.Weather.class)).requestUpdateAll();
   return;
  }
  if("long_title".equals(intent.getStringExtra("command"))){
   context.getSharedPreferences("fixture",0).edit().putBoolean("long_title",intent.getBooleanExtra("enabled",false)).commit();
   androidx.wear.watchface.complications.datasource.ComplicationDataSourceUpdateRequester.create(context,new ComponentName(context,FixtureService.Heart.class)).requestUpdateAll();
   return;
  }
  if("alternate".equals(intent.getStringExtra("command"))){
   context.getSharedPreferences("fixture",0).edit().putBoolean("alternate",intent.getBooleanExtra("enabled",false)).commit();
   androidx.wear.watchface.complications.datasource.ComplicationDataSourceUpdateRequester.create(context,new ComponentName(context,FixtureService.Heart.class)).requestUpdateAll();
   return;
  }
  if(EditorAccessibilityService.instance!=null)EditorAccessibilityService.instance.command(intent.getStringExtra("command"),intent.getStringExtra("text"));
 }
}

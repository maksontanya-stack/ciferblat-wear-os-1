package ru.meta.wearos.classic1.fixtures;
import android.accessibilityservice.AccessibilityService;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.util.Log;
public class EditorAccessibilityService extends AccessibilityService {
 public static EditorAccessibilityService instance;
 @Override protected void onServiceConnected(){ instance=this; }
 @Override public void onAccessibilityEvent(AccessibilityEvent event){}
 @Override public void onInterrupt(){}
 public void command(String action,String text){
  AccessibilityNodeInfo root=getRootInActiveWindow(); if(root==null)return;
  if(action.equals("next") || action.equals("previous")){
   for(AccessibilityNodeInfo node: root.findAccessibilityNodeInfosByViewId("com.google.android.wearable.sysui:id/wf_editor_pager2"))
    Log.i("EDITOR_TEST", action+"="+node.performAction(action.equals("next")?AccessibilityNodeInfo.ACTION_SCROLL_FORWARD:AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD));
  } else if(action.equals("tap")) {
   for(AccessibilityNodeInfo node:root.findAccessibilityNodeInfosByText(text)){
    while(node!=null && !node.isClickable())node=node.getParent();
    if(node!=null){Log.i("EDITOR_TEST","tap="+node.performAction(AccessibilityNodeInfo.ACTION_CLICK));break;}
   }
  }
 }
}

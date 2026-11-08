package ru.meta.wearos.classic1.fixtures;
import android.accessibilityservice.AccessibilityService;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.util.Log;
import android.graphics.Rect;
import android.util.Xml;
import org.xmlpull.v1.XmlSerializer;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
public class EditorAccessibilityService extends AccessibilityService {
 public static EditorAccessibilityService instance;
 @Override protected void onServiceConnected(){ instance=this; }
 @Override public void onAccessibilityEvent(AccessibilityEvent event){}
 @Override public void onInterrupt(){}
 private void node(XmlSerializer xml, AccessibilityNodeInfo value) throws Exception {
  if(value==null)return;
  Rect bounds=new Rect();value.getBoundsInScreen(bounds);
  xml.startTag(null,"node");
  xml.attribute(null,"text",value.getText()==null?"":value.getText().toString());
  xml.attribute(null,"content-desc",value.getContentDescription()==null?"":value.getContentDescription().toString());
  xml.attribute(null,"resource-id",value.getViewIdResourceName()==null?"":value.getViewIdResourceName());
  xml.attribute(null,"clickable",Boolean.toString(value.isClickable()));
  xml.attribute(null,"scrollable",Boolean.toString(value.isScrollable()));
  xml.attribute(null,"bounds","["+bounds.left+","+bounds.top+"]["+bounds.right+","+bounds.bottom+"]");
  for(int i=0;i<value.getChildCount();i++)node(xml,value.getChild(i));
  xml.endTag(null,"node");
 }
 public void command(String action,String text){
  AccessibilityNodeInfo root=getRootInActiveWindow(); if(root==null)return;
  if(action.equals("dump")){
   try {
    StringWriter writer=new StringWriter();XmlSerializer xml=Xml.newSerializer();xml.setOutput(writer);xml.startDocument("UTF-8",true);xml.startTag(null,"hierarchy");node(xml,root);xml.endTag(null,"hierarchy");xml.endDocument();
    try(java.io.FileOutputStream file=openFileOutput("window.xml",MODE_PRIVATE)){file.write(writer.toString().getBytes(StandardCharsets.UTF_8));}
   } catch(Exception error){throw new RuntimeException(error);}
   return;
  }
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

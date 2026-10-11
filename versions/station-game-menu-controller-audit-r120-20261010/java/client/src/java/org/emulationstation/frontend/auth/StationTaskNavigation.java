package org.emulationstation.frontend.auth;

import android.app.Activity;
import android.app.ActivityManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import java.util.ArrayList;
import java.util.List;

/** Main-process navigation only. No task removal, process termination or server commands. */
public final class StationTaskNavigation {
    private static Object gameOwner;private static int gameTask=-1;
    private static String pendingTarget;private static int pendingTask=-1;
    private StationTaskNavigation(){}
    public static synchronized void gameVisible(Object owner,int task){gameOwner=owner;gameTask=task;}
    public static synchronized void gameEnded(Object owner){if(gameOwner==owner){gameOwner=null;gameTask=-1;}}
    /** The lobby's existing returningFromGame branch is a completed native return. */
    public static synchronized void gameReturned(Activity lobby){if(gameTask==lobby.getTaskId()){gameOwner=null;gameTask=-1;}}
    private static synchronized int registeredGame(){return gameTask;}
    public static synchronized void arrived(Activity activity){
        if(activity.getClass().getName().equals(pendingTarget)){pendingTarget=null;pendingTask=-1;}
    }
    private static final class Tasks {
        final List<ActivityManager.AppTask> handles=new ArrayList<>();
        final List<StationTaskPolicy.Task> values=new ArrayList<>();
        StationTaskPolicy.Task[] array(){return values.toArray(new StationTaskPolicy.Task[0]);}
        ActivityManager.AppTask handle(int id){for(int i=0;i<values.size();i++)if(values.get(i).id==id)return handles.get(i);return null;}
    }
    private static Tasks tasks(Activity activity){
        Tasks result=new Tasks();ActivityManager manager=(ActivityManager)activity.getSystemService(Context.ACTIVITY_SERVICE);
        if(manager==null)return result;
        try{for(ActivityManager.AppTask task:manager.getAppTasks())try{
            ActivityManager.RecentTaskInfo info=task.getTaskInfo();ComponentName base=info.baseActivity,top=info.topActivity;
            boolean owned=base!=null&&top!=null&&activity.getPackageName().equals(base.getPackageName())&&activity.getPackageName().equals(top.getPackageName());
            result.handles.add(task);result.values.add(new StationTaskPolicy.Task(info.id,base==null?null:base.getClassName(),top==null?null:top.getClassName(),owned,info.numActivities>0));
        }catch(RuntimeException stale){/* An independently finishing task is skipped. */}}catch(RuntimeException unavailable){/* Cold launch remains available. */}
        return result;
    }
    private static boolean move(Tasks tasks,int id){
        ActivityManager.AppTask task=tasks.handle(id);if(task==null)return false;
        try{task.moveToFront();return true;}catch(RuntimeException stale){return false;}
    }
    /** Call only after the existing authorization and storage checks succeeded. */
    public static boolean resumeExistingTask(Activity activity){Tasks current=tasks(activity);return move(current,StationTaskPolicy.resumeTask(current.array(),registeredGame()));}
    public static boolean resumeRunningGame(Activity activity){Tasks current=tasks(activity);return move(current,StationTaskPolicy.gameTask(current.array(),registeredGame()));}
    /** Every internal networking entry uses this one main-thread route. */
    public static boolean open(Activity activity,Intent intent){
        if(activity==null||activity.isFinishing()||activity.isDestroyed())return false;
        ComponentName target=intent.getComponent();if(target==null||!activity.getPackageName().equals(target.getPackageName()))return false;
        String name=target.getClassName();if(!StationTaskPolicy.ROOMS.equals(name)&&!StationTaskPolicy.NETPLAY.equals(name))return false;
        Tasks current=tasks(activity);int game=StationTaskPolicy.gameTask(current.array(),registeredGame());
        if(game>=0)return move(current,game); // Keep the running game above its lobby.
        synchronized(StationTaskNavigation.class){if(name.equals(pendingTarget)&&pendingTask==activity.getTaskId())return true;pendingTarget=name;pendingTask=activity.getTaskId();}
        intent.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT|Intent.FLAG_ACTIVITY_SINGLE_TOP);
        try{
            for(StationTaskPolicy.Task task:current.values)if(StationTaskPolicy.usable(task)&&(name.equals(task.top)||name.equals(task.base))){
                current.handle(task.id).startActivity(activity,intent,null);return true;
            }
            activity.startActivity(intent);return true;
        }catch(RuntimeException refused){synchronized(StationTaskNavigation.class){pendingTarget=null;pendingTask=-1;}return false;}
    }
}

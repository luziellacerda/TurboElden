package android.os;public interface IBinder{interface DeathRecipient{void binderDied();}void linkToDeath(DeathRecipient d,int f)throws RemoteException;boolean unlinkToDeath(DeathRecipient d,int f);}

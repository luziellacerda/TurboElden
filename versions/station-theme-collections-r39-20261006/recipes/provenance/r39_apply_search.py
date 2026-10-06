from pathlib import Path
import shutil
W=Path(r'E:\ESTUDO APK\work\station-theme-collections-r39-20261006');N=W/'native'
for src,dst in [('r39_search_state.h','native_search_state.h'),('r39_search_actions.h','station_search_actions.h')]:shutil.copy2(src,N/dst)
p=N/'native_carousel.cpp';s=p.read_text('utf8')
s=s.replace('static bool starts(const char*t', '#include "native_search_state.h"\nstatic bool starts(const char*t',1)
s=s.replace('static void invalidate(void*p){','static void invalidate(void*p){\n stationEmptySearchCache.invalidate();',1)
start=s.index(' // The native full-text branch admits');end=s.index('\n}\nstatic void refreshHook',start)
s=s[:start]+''' // A zero-result search is a valid cached result. The original routine otherwise
 // scans/allocates again every frame because its visible vector is empty.
 void*catalog=systemsMode?(folderMode?(void*)folderFacade:(void*)facade):fn<void*(*)()>(0x1887dc)();
 if(stationEmptySearchCache.reuse(p,catalog))return;
 fn<V>(0x21b134)(p);
 U originalEnd=at<U>(p,0x100);
 if(!systemsMode)stationSearchScope(p,catalog);
 filterFolderGames(p);
 if(originalEnd!=at<U>(p,0x100))refreshHook(p);
 stationEmptySearchCache.remember(p,catalog);'''+s[end:]
s=s.replace('static void showSystems(void*p){','static void showSystems(void*p){\n clearSearchForNavigation(p);',1)
s=s.replace('pauseSystemVideo720();lastSystem=(int)index;', 'clearSearchForNavigation(p);pauseSystemVideo720();lastSystem=(int)index;',1)
s=s.replace('strAssign((B*)p+0x650,"");','')
anchor=' if(at<int>((void*)in,12)&&!modal(p)&&at<int>(p,0x370)>=2){'
s=s.replace(anchor,''' if(at<int>((void*)in,12)&&stationSearchCanBack(p)&&(rawKey==27||rawKey==0x4000010e||mapped(cfg,"b",in))){
  unsigned tick=fn<unsigned(*)()>(0x39e240)();
  if(handledBack&&(unsigned)(tick-lastBackTick)<250)return true;
  handledBack=true;lastBackTick=tick;stationSearchBack(p);return true;
 }
'''+anchor,1)
s=s.replace('gui=p;settingsChatbotPress(p,event);','gui=p;if(touchSearchRecovery(p,event))return true;settingsChatbotPress(p,event);',1)
p.write_text(s,'utf8')
p=N/'native_folders.h';s=p.read_text('utf8')
s=s.replace(' clearTextures(p);releaseFolderListing();',' clearSearchForNavigation(p);clearTextures(p);releaseFolderListing();',1)
s=s.replace(' clearTextures(p);folderReturnKind=returnKind;', ' clearSearchForNavigation(p);clearTextures(p);folderReturnKind=returnKind;',1)
s=s.replace('strAssign((B*)p+0x650,"");','');p.write_text(s,'utf8')
p=N/'native_search_download.h';s=p.read_text('utf8').replace('storeUiLabels[51]','storeUiLabels[57]').replace('slot>=51','slot>=57')
s='#include "station_search_actions.h"\n'+s
pos=s.index('static void layoutSearchPresentation(void*p)')
s=s[:pos]+'''static StationSearchGesture stationSearchGesture;
static bool touchSearchRecovery(void*p,const void*event){
 bool editor=at<B>(p,0x648)!=0;
 bool enabled=!stationSearchOtherModal(p)&&((editor&&!at<B>(p,0x598))||stationSearchEmpty(p));
 int action=stationSearchGesture.touch(at<int>((void*)event,0),at<U>((void*)event,8),at<float>((void*)event,0x10),at<float>((void*)event,0x14),at<float>(p,0x54),at<float>(p,0x58),editor,enabled);
 if(action<0)return false;
 if(action==1)fn<void(*)(void*,bool)>(0x219570)(p,true);
 if(action==2){if(editor)fn<void(*)(void*,bool)>(0x219570)(p,false);else searchHook(p);}
 return true;
}
static void paintSearchActions(void*p,const void*m,bool editor){
 float w=at<float>(p,0x54),h=at<float>(p,0x58);
 for(int a=1;a<=2;a++){
  auto r=stationSearchActionBox(w,h,editor,a);UiBox b{r.x,r.y,r.w,r.h};
  uiSurface(b,a==1?0x163323ff:0x182B3Dff,a==1?0x47D887ff:0x669EDAff);
  uiLabel(p,50+a,a==1?"LIMPAR PESQUISA":editor?"VER RESULTADOS":"EDITAR PESQUISA",m,b,.79f,0xECFFF5ff,1);
 }
}
static void paintSearchEmpty(void*p,const void*m){
 if(!stationSearchEmpty(p))return;
 float w=at<float>(p,0x54),h=at<float>(p,0x58);uiMatrix(m);
 uiLabel(p,53,systemsMode?(folderMode?"NENHUMA COLEÇÃO ENCONTRADA":"NENHUMA PLATAFORMA ENCONTRADA"):"NENHUM JOGO ENCONTRADO",m,{w*.37f,h*.35f,w*.57f,h*.075f},1.1f,0xF0FFF6ff);
 uiLabel(p,54,"Altere o nome ou limpe a pesquisa para mostrar esta lista novamente.",m,{w*.375f,h*.442f,w*.56f,h*.066f},.8f,0xB8CEBEff);
 paintSearchActions(p,m,false);uiMatrix(m);
}
'''+s[pos:]
s=s.replace('h*(pad?.744f:.245f)','h*(pad?.744f:.342f)',1)
s=s.replace(' }else uiLabel(p,47,"Os resultados mudam enquanto você digita."', ' }else {paintSearchActions(p,m,true);uiLabel(p,47,"Os resultados mudam enquanto você digita."',1)
s=s.replace('},.63f,0x88A793ff);\n uiMatrix(m);','},.63f,0x88A793ff);}\n uiMatrix(m);',1)
s=s.replace(' paintSearchModal(p,m);',' paintSearchEmpty(p,m);paintSearchModal(p,m);',1)
p.write_text(s,'utf8')
print('Search state, scope, Android Back and native recovery UI updated')

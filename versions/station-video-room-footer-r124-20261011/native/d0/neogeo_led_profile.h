// Explicit platform identity; source-frame signature is still mandatory.
static bool neoMagazineKey(const char*key){
 if(!key)return false;
 const char*names[]={"Neo Geo","Neo Geo CD","neogeo","neogeocd","neo-geo","neo-geo-cd"};
 for(const char*name:names)if(presentationKeyEqual(key,name))return true;
 return false;
}

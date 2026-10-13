
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <climits>
#include <string>
#include <map>
#define MAX_USERS 16
#define RARCH_FIRST_CUSTOM_BIND 16
#define RARCH_UNMAPPED UINT_MAX
#define RETROK_UNKNOWN 0
#define RETRO_DEVICE_NONE 0
#define RETRO_DEVICE_JOYPAD 1
#define INP_FLAG_REMAPPING_CACHE_ACTIVE 1
struct settings_t { struct { unsigned input_remap_ids[16][24],input_keymapper_ids[16][24],input_libretro_device[16],input_analog_dpad_mode[16],input_remap_ports[16],input_turbo_mode,input_turbo_button,input_turbo_period,input_turbo_duty_cycle; } uints; struct {bool input_turbo_enable,input_turbo_allow_dpad;} bools;struct {int input_turbo_bind;} ints;};
static settings_t store,*config_st=&store;
struct runloop_state_t {struct {char* remapfile;} name;};static runloop_state_t rs;
struct input_state_t {unsigned flags;};static input_state_t is;
struct config_file_t {std::map<std::string,int> ints;};
static runloop_state_t* runloop_state_get_ptr(){return &rs;}
static input_state_t* input_state_get_ptr(){return &is;}
static bool string_is_empty(const char* s){return !s||!*s;}
static size_t strlcpy(char* d,const char* s,size_t n){size_t z=strlen(s);if(n){size_t c=z<n-1?z:n-1;memcpy(d,s,c);d[c]=0;}return z;}
static void fill_pathname_join_delim(char*d,const char*a,const char*b,char c,size_t n){snprintf(d,n,"%s%c%s",a,c,b);}
static bool config_get_int(config_file_t*c,const char*k,int*v){auto i=c->ints.find(k);if(i==c->ints.end())return false;*v=i->second;return true;}
#define configuration_set_uint(s,x,v) ((x)=(v))
#define CONFIG_GET_INT_BASE(c,s,f,k) do{int v;if(config_get_int(c,k,&v))(s)->f=v;}while(0)
#define CONFIG_GET_BOOL_BASE(c,s,f,k) do{int v;if(config_get_int(c,k,&v))(s)->f=v!=0;}while(0)
static void input_remapping_deinit(bool){free(rs.name.remapfile);rs.name.remapfile=nullptr;}
static void input_remapping_update_port_map(){}
static void input_remapping_set_defaults(bool){for(unsigned i=0;i<16;i++){store.uints.input_remap_ports[i]=i;for(unsigned j=0;j<24;j++)store.uints.input_remap_ids[i][j]=j;}}
struct retro_controller_description {const char* desc;unsigned id;};
struct retro_controller_info {const retro_controller_description*types;unsigned num_types;};
struct rarch_system_info_t {struct {unsigned size;retro_controller_info data[2];}ports;};
struct retro_ctx_controller_info_t {unsigned port,device;};
static unsigned connected[2];
static unsigned input_config_get_device(unsigned p){return store.uints.input_libretro_device[p];}
static const retro_controller_description* libretro_find_controller_description(const retro_controller_info* p,unsigned id){for(unsigned i=0;i<p->num_types;i++)if(p->types[i].id==id)return &p->types[i];return nullptr;}
static bool core_set_controller_port_device(retro_ctx_controller_info_t*p){if(p->port<2)connected[p->port]=p->device;return true;}
#define RARCH_WARN(...) ((void)0)

bool input_remapping_load_file(void *data, const char *path)
{
   unsigned i, j;
   config_file_t *conf                              = (config_file_t*)data;
   settings_t *settings                             = config_st;
   runloop_state_t *runloop_st                      = runloop_state_get_ptr();
   char key_strings[RARCH_FIRST_CUSTOM_BIND + 8][8] =
   {
      "b",      "y",      "select", "start",
      "up",     "down",   "left",   "right",
      "a",      "x",      "l",      "r",
      "l2",     "r2",     "l3",     "r3",
      "l_x+",   "l_x-",   "l_y+",   "l_y-",
      "r_x+",   "r_x-",   "r_y+",   "r_y-"
   };

   if (    !conf
         || string_is_empty(path))
      return false;

   if (!string_is_empty(runloop_st->name.remapfile))
      input_remapping_deinit(false);

   input_remapping_set_defaults(false);
   runloop_st->name.remapfile = strdup(path);

   for (i = 0; i < MAX_USERS; i++)
   {
      size_t _len;
      char prefix[16];
      char s1[32], s2[32], s3[32];
      char formatted_number[4];
      formatted_number[0] = '\0';
      snprintf(formatted_number, sizeof(formatted_number), "%u", i + 1);
      _len       = strlcpy(prefix, "input_player",   sizeof(prefix));
      strlcpy(prefix + _len, formatted_number, sizeof(prefix) - _len);
      _len       = strlcpy(s1, prefix, sizeof(s1));
      strlcpy(s1 + _len, "_btn", sizeof(s1) - _len);
      _len       = strlcpy(s2, prefix, sizeof(s2));
      strlcpy(s2 + _len, "_key", sizeof(s2) - _len);
      _len       = strlcpy(s3, prefix, sizeof(s3));
      strlcpy(s3 + _len, "_stk", sizeof(s3) - _len);

      for (j = 0; j < RARCH_FIRST_CUSTOM_BIND + 8; j++)
      {
         const char *key_string = key_strings[j];

         if (j < RARCH_FIRST_CUSTOM_BIND)
         {
            char ident[128];
            int _remap = -1;

            fill_pathname_join_delim(ident, s1,
                  key_string, '_', sizeof(ident));

            if (config_get_int(conf, ident, &_remap))
            {
               if (_remap == -1)
                  _remap = RARCH_UNMAPPED;

               configuration_set_uint(settings,
                     settings->uints.input_remap_ids[i][j], _remap);
            }

            fill_pathname_join_delim(ident, s2,
                  key_string, '_', sizeof(ident));

            _remap = -1;

            if (!config_get_int(conf, ident, &_remap))
               _remap = RETROK_UNKNOWN;

            configuration_set_uint(settings,
                  settings->uints.input_keymapper_ids[i][j], _remap);
         }
         else
         {
            char ident[256];
            int _remap = -1;

            fill_pathname_join_delim(ident, s3,
                  key_string, '_', sizeof(ident));

            if (config_get_int(conf, ident, &_remap))
            {
               if (_remap == -1)
                  _remap = RARCH_UNMAPPED;

               configuration_set_uint(settings,
                     settings->uints.input_remap_ids[i][j], _remap);
            }

            fill_pathname_join_delim(ident, s2,
                  key_string, '_', sizeof(ident));

            _remap = -1;

            if (!config_get_int(conf, ident, &_remap))
               _remap = RETROK_UNKNOWN;

            configuration_set_uint(settings,
                  settings->uints.input_keymapper_ids[i][j], _remap);
         }
      }

      _len = strlcpy(s1, "input_libretro_device_p", sizeof(s1));
      strlcpy(s1 + _len, formatted_number, sizeof(s1) - _len);
      CONFIG_GET_INT_BASE(conf, settings, uints.input_libretro_device[i], s1);

      _len = strlcpy(s1, prefix, sizeof(s1));
      strlcpy(s1 + _len, "_analog_dpad_mode", sizeof(s1) - _len);
      CONFIG_GET_INT_BASE(conf, settings, uints.input_analog_dpad_mode[i], s1);

      _len = strlcpy(s1, "input_remap_port_p", sizeof(s1));
      strlcpy(s1 + _len, formatted_number, sizeof(s1) - _len);
      CONFIG_GET_INT_BASE(conf, settings, uints.input_remap_ports[i], s1);
   }

   /* Turbo fire settings */
   CONFIG_GET_BOOL_BASE(conf, settings, bools.input_turbo_enable, "input_turbo_enable");
   CONFIG_GET_BOOL_BASE(conf, settings, bools.input_turbo_allow_dpad, "input_turbo_allow_dpad");
   CONFIG_GET_INT_BASE(conf, settings, uints.input_turbo_mode, "input_turbo_mode");
   CONFIG_GET_INT_BASE(conf, settings, ints.input_turbo_bind, "input_turbo_bind");
   CONFIG_GET_INT_BASE(conf, settings, uints.input_turbo_button, "input_turbo_button");
   CONFIG_GET_INT_BASE(conf, settings, uints.input_turbo_period, "input_turbo_period");
   CONFIG_GET_INT_BASE(conf, settings, uints.input_turbo_duty_cycle, "input_turbo_duty_cycle");

   input_remapping_update_port_map();

   /* Whenever a remap file is loaded, subsequent
    * changes to global remap-related parameters
    * must be reset at the next core deinitialisation */
   input_state_get_ptr()->flags   |=  INP_FLAG_REMAPPING_CACHE_ACTIVE;

   return true;
}
void command_event_init_controllers(rarch_system_info_t *sys_info,
      settings_t *settings, unsigned num_active_users)
{
   unsigned port;
   unsigned num_core_ports = sys_info->ports.size;

   for (port = 0; port < num_core_ports; port++)
   {
      size_t i;
      retro_ctx_controller_info_t pad;
      unsigned device                                 = RETRO_DEVICE_NONE;
      const struct retro_controller_description *desc = NULL;

      /* Check whether current core port is mapped
       * to an input device
       * > If is not, leave 'device' set to
       *   'RETRO_DEVICE_NONE'
       * > For example: if input ports 0 and 1 are
       *   mapped to core port 0, core port 1 will
       *   be unmapped and should be disabled */
      for (i = 0; i < num_active_users; i++)
      {
         if (i >= MAX_USERS)
            break;

         if (port == settings->uints.input_remap_ports[i])
         {
            device = input_config_get_device(port);
            break;
         }
      }

      desc = libretro_find_controller_description(
            &sys_info->ports.data[port], device);

      if (desc && !desc->desc)
      {
         /* If we're trying to connect a completely unknown device,
          * revert back to JOYPAD. */
         if (device != RETRO_DEVICE_JOYPAD && device != RETRO_DEVICE_NONE)
         {
            /* Do not fix device,
             * because any use of dummy core will reset this,
             * which is not a good idea. */
            RARCH_WARN("[Input] Input device ID %u is unknown to this "
                  "libretro implementation. Using RETRO_DEVICE_JOYPAD.\n",
                  device);
            device = RETRO_DEVICE_JOYPAD;
         }
      }

      pad.device     = device;
      pad.port       = port;
      core_set_controller_port_device(&pad);
   }
}

int main(){
 const retro_controller_description a[]={{"Joypad",1}},b[]={{"Joypad",1},{"Multitap",257}};
 rarch_system_info_t sys{{2,{{a,1},{b,2}}}};
 unsigned cases=0;
 for(unsigned count=2;count<=2;count++){
  memset(&store,0,sizeof(store));for(unsigned i=0;i<16;i++)store.uints.input_libretro_device[i]=1;
  input_remapping_set_defaults(false);command_event_init_controllers(&sys,&store,16);
  if(connected[1]!=1)return 1; // cfg keys do not enter the remap reader
  config_file_t room;unsigned devices[]={1,257,1,1,1};
  for(unsigned i=0;i<16;i++)room.ints["input_libretro_device_p"+std::to_string(i+1)]=i<5?devices[i]:0;
  if(!input_remapping_load_file(&room,"private/bsnes-mercury/bsnes-mercury.rmp"))return 2;
  command_event_init_controllers(&sys,&store,16);
  if(connected[0]!=1||connected[1]!=257)return 3;
  for(unsigned i=0;i<16;i++){if(store.uints.input_libretro_device[i]!=(i<5?devices[i]:0)||store.uints.input_remap_ports[i]!=i)return 4;for(unsigned j=0;j<24;j++)if(store.uints.input_remap_ids[i][j]!=j||store.uints.input_keymapper_ids[i][j]!=0)return 5;}
  if(store.bools.input_turbo_enable||store.bools.input_turbo_allow_dpad||store.uints.input_turbo_mode)return 6;
  input_remapping_deinit(false);cases++;
 }
 puts("cases=1 actualRemapLoader=true actualControllerInit=true adapter=257 unrelatedButtonMappingsPreserved=true");
}

/* Copyright  (C) 2010-2020 The RetroArch team
 *
 * ---------------------------------------------------------------------------------------
 * The following license statement only applies to this file (config_file.c).
 * ---------------------------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge,
 * to any person obtaining a copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */


#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cctype>
#include <cassert>
#include <string>
#include <file/config_file.h>
#include <array/rhmap.h>
#define MAX_INCLUDE_DEPTH 16
static char *strtok_r(char*a,const char*b,char**c){return strtok_s(a,b,c);}
#define PATH_MAX_LENGTH 4096
#define STRLEN_CONST(s) (sizeof(s)-1)
#define ISSPACE(x) isspace(x)
static bool string_is_empty(const char*s){return !s||!*s;}
static bool string_is_equal(const char*a,const char*b){return a&&b&&!strcmp(a,b);}
static bool string_starts_with_size(const char*a,const char*b,size_t n){return !strncmp(a,b,n);}
static size_t strlcpy(char*d,const char*s,size_t n){size_t z=strlen(s);if(n){size_t c=z<n-1?z:n-1;memcpy(d,s,c);d[c]=0;}return z;}
static void config_file_add_sub_conf(config_file_t*,char*,char*,size_t,config_file_cb_t*){assert(false);}
void config_file_initialize(config_file_t*c){memset(c,0,sizeof(*c));}
static int config_file_load_internal(config_file_t*,const char*,unsigned,config_file_cb_t*){assert(false);return -1;}
static void config_file_add_child_list(config_file_t*,config_file_t*){assert(false);}
bool config_file_deinitialize(config_file_t*){assert(false);return false;}
size_t config_file_add_reference(config_file_t*,char*){assert(false);return 0;}

static char *config_file_strip_comment(char *str)
{
   /* Search for a comment (#) character */
   char *comment = strchr(str, '#');

   if (comment)
   {
      char *literal_start = NULL;

      /* Check whether entire line is a comment
       * > First character == '#' */
      if (str == comment)
      {
         /* Set 'str' to NUL and return comment
          * for processing at a higher level */
         *str = '\0';
         return ++comment;
      }

      /* Comment character occurs at an offset:
       * Search for the start of a string literal value */
      literal_start = strchr(str, '\"');

      /* Check whether string literal start occurs
       * *before* the comment character */
      if (literal_start && (literal_start < comment))
      {
         /* Search for the end of the string literal
          * value */
         char *literal_end = strchr(literal_start + 1, '\"');

         /* Check whether string literal end occurs
          * *after* the comment character
          * > If this is the case, ignore the comment
          * > Leave 'str' untouched and return NULL */
         if (literal_end && (literal_end > comment))
            return NULL;
      }

      /* If we reach this point, then a comment
       * exists outside of a string literal
       * > Trim the entire comment from the end
       *   of 'str' */
      *comment = '\0';
   }

   return NULL;
}
static char *config_file_extract_value(char *line)
{
   char *dst = NULL;
   while (ISSPACE((int)*line))
      line++;

   /* Note: From this point on, an empty value
    * string is valid - and in this case, strldup("", sizeof(""))
    * will be returned (see Note 2)
    * > If we instead return NULL, the the entry
    *   is ignored completely - which means we cannot
    *   track *changes* in entry value */

   /* If first character is ("), we have a full string
    * literal */
   if (*line == '"')
   {
      size_t idx  = 0;
      char *value = NULL;
      /* Skip to next character */
      line++;

      /* If this a ("), then value string is empty */
      if (*line != '"')
      {
         /* Find the next (") character */
         while (line[idx] && (line[idx] != '\"'))
            idx++;

         line[idx] = '\0';
         if ((value = line) && *value)
            return strdup(value);
      }
   }
   /* This is not a string literal - just read
    * until the next space is found
    * > Note: Skip this if line is empty */
   else if (*line != '\0')
   {
      size_t idx  = 0;
      char *value = NULL;
      /* Find next space character */
      while (line[idx] && isgraph((int)line[idx]))
         idx++;

      line[idx] = '\0';
      if ((value = line) && *value)
         return strdup(value);
   }

   /* Note 2: This is an unrolled strldup call
    * to avoid an unnecessary dependency -
    * call is strldup("", sizeof(""))
    **/
   dst = (char*)malloc(sizeof(char) * 2);
   strlcpy(dst, "", 1);
   return dst;
}
static bool config_file_parse_line(config_file_t *conf,
      struct config_entry_list *list, char *line, config_file_cb_t *cb)
{
   size_t cur_size       = 32;
   size_t idx            = 0;
   char *key             = NULL;
   char *key_tmp         = NULL;
   /* Remove any comment text */
   char *comment         = config_file_strip_comment(line);

   /* Check whether entire line is a comment */
   if (comment)
   {
      char *path               = NULL;
      bool include_found       = string_starts_with_size(comment,
            "include ",   STRLEN_CONST("include "));
      bool reference_found     = string_starts_with_size(comment,
            "reference ", STRLEN_CONST("reference "));

      /* All comments except those starting with the include or
       * reference directive are ignored */
      if (!include_found && !reference_found)
         return false;

      /* Starting a line with an 'include' directive
       * appends a sub-config file */
      if (include_found)
      {
         config_file_t sub_conf;
         char real_path[PATH_MAX_LENGTH];
         char *include_line = comment + STRLEN_CONST("include ");

         if (string_is_empty(include_line))
            return false;

         if (!(path = config_file_extract_value(include_line)))
            return false;

         if (     string_is_empty(path)
               || conf->include_depth >= MAX_INCLUDE_DEPTH)
         {
            free(path);
            return false;
         }

         config_file_add_sub_conf(conf, path,
            real_path, sizeof(real_path), cb);

         config_file_initialize(&sub_conf);

         switch (config_file_load_internal(&sub_conf, real_path,
            conf->include_depth + 1, cb))
         {
            case 0:
               /* Pilfer internal list. */
               config_file_add_child_list(conf, &sub_conf);
               /* fall-through to deinitialize */
            case -1:
               config_file_deinitialize(&sub_conf);
               break;
            case 1:
            default:
               break;
         }
      }

      /* Starting a line with an 'reference' directive
       * sets the reference path */
      if (reference_found)
      {
         char *reference_line = comment + STRLEN_CONST("reference ");

         if (string_is_empty(reference_line))
            return false;

         if (!(path = config_file_extract_value(reference_line)))
            return false;

         config_file_add_reference(conf, path);

         if (!path)
            return false;
      }

      free(path);
      return true;
   }

   /* Skip to first non-space character */
   while (ISSPACE((int)*line))
      line++;

   /* Allocate storage for key */
   if (!(key = (char*)malloc(cur_size + 1)))
      return false;

   /* Copy line contents into key until we
    * reach the next space character */
   while (isgraph((int)*line))
   {
      /* If current key storage is too small,
       * double its size */
      if (idx == cur_size)
      {
         cur_size *= 2;
         if (!(key_tmp   = (char*)realloc(key, cur_size + 1)))
         {
            free(key);
            return false;
         }

         key     = key_tmp;
      }

      key[idx++] = *line++;
   }
   key[idx]      = '\0';

   /* Add key and value entries to list */
   list->key     = key;

   /* An entry without a value is invalid */
   while (ISSPACE((int)*line))
      line++;

   /* If we don't have an equal sign here,
    * we've got an invalid string. */
   if (*line != '=')
   {
      list->value = NULL;
      list->key   = NULL;
      free(key);
      return false;
   }

   line++;

   if (!(list->value   = config_file_extract_value(line)))
   {
      list->key   = NULL;
      free(key);
      return false;
   }

   return true;
}
static int config_file_from_string_internal(
      struct config_file *conf,
      char *from_string,
      const char *path)
{
   char *lines                    = from_string;
   char *save_ptr                 = NULL;
   char *line                     = NULL;

   if (!string_is_empty(path))
      conf->path                  = strdup(path);
   if (string_is_empty(lines))
      return 0;

   /* Get first line of config file */
   line = strtok_r(lines, "\n", &save_ptr);

   while (line)
   {
      struct config_entry_list *list = (struct config_entry_list*)
            malloc(sizeof(*list));

      if (!list)
         return -1;

      list->readonly  = false;
      list->key       = NULL;
      list->value     = NULL;
      list->next      = NULL;

      /* Parse current line */
      if (
              !string_is_empty(line)
            && config_file_parse_line(conf, list, line, NULL))
      {
         if (conf->entries)
            conf->tail->next = list;
         else
            conf->entries    = list;

         conf->tail          = list;

         if (list->key)
         {
            /* Only add entry to the map if an entry
             * with the specified value does not
             * already exist */
            uint32_t hash = rhmap_hash_string(list->key);
            if (!RHMAP_HAS_FULL(conf->entries_map, hash, list->key))
               RHMAP_SET_FULL(conf->entries_map, hash, list->key, list);
         }
      }

      if (list != conf->tail)
         free(list);

      /* Get next line of config file */
      line = strtok_r(NULL, "\n", &save_ptr);
   }

   return 0;
}
struct config_entry_list *config_get_entry(
      const config_file_t *conf, const char *key)
{
   return RHMAP_GET_STR(conf->entries_map, key);
}
bool config_get_bool(config_file_t *conf, const char *key, bool *in)
{
   const struct config_entry_list *entry = config_get_entry(conf, key);

   if (!entry)
      return false;

   if      (
         (
            entry->value[0] == '1'
         && entry->value[1] == '\0'
         )
         || string_is_equal(entry->value, "true")
         )
      *in = true;
   else if (
         (
            entry->value[0] == '0'
         && entry->value[1] == '\0'
         )
         || string_is_equal(entry->value, "false")
         )
      *in = false;
   else
      return false;

   return true;
}

static bool read(const char*txt){config_file_t c{};char*b=strdup(txt);assert(config_file_from_string_internal(&c,b,"room/retroarch.cfg")==0);bool result=true;assert(config_get_bool(&c,"auto_remaps_enable",&result));free(b);return result;}
int main(){
 const char* old="auto_remaps_enable = \"false\"\ninput_remapping_directory = \"room/input-devices\"\nauto_remaps_enable = \"true\"\n";
 assert(!read(old));
 assert(read("auto_remaps_enable = \"true\"\ninput_remapping_directory = \"room/input-devices\"\n"));
 assert(!read("auto_remaps_enable = \"false\"\n"));
 puts("actualParser=true duplicateFalseThenTrue=false uniqueTrue=true unrelatedFalse=false cases=3");
}

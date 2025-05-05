// lab10
// fall 2023
// name: Aarav Mehta
//

// includes
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include "lab10.h"
#include <stdlib.h>

//global variables
int exiting = 0;
pthread_mutex_t mutex_bin = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t mutex_list = PTHREAD_MUTEX_INITIALIZER;
unsigned char enckey;

//argument struct
struct arg_struct {
  char * txtfile;
  char * binfile;
};

// defines

// main
int main (int argc, char* argv[])
{
  
  //declaring variables
  pthread_t main_t;
  pthread_t autosave_t;
  struct arg_struct arguments;


  if(argc < 4){
    printf("Missing filenames\n");
    return 1;
  }
  arguments.txtfile = argv[1];
  arguments.binfile = argv[2];
  enckey = atoi(argv[3]);

  pthread_create(&main_t, NULL, main_thread, (void*)&arguments);
  pthread_create(&autosave_t, NULL, autosave_thread, (void*)argv[2]);
  pthread_join(main_t, NULL);
  pthread_cancel(autosave_t);
  delete_heads();
}

//main thread
void * main_thread(void * arg){
  struct arg_struct * arguments = (struct arg_struct*)arg;
  char *txtfile = arguments->txtfile;
  char *binfile = arguments->binfile;

  int  option;
  char del_fname[20];
  char del_lname[20];
  char del_all[20];
  
  read_from_file(txtfile);
  
  while (1)
    {
      printf ("\nEnter a number: 1 (insert), 2 (show all), 3 (show name), 4(delete), 5(delete name), 6(show binary) or 0 (quit): ");
    
    
      if (scanf ("%d", &option) != 1)
      {
        printf ("error\n");
        return 0;
      }
      
      switch (option)
        {
        case 1:
          pthread_mutex_lock(&mutex_list);
          read_from_keyboard();
          pthread_mutex_unlock(&mutex_list);
          break;
        
        case 2:
          pthread_mutex_lock(&mutex_list);
          show_all();
          pthread_mutex_unlock(&mutex_list);
          break;

        case 3:
          pthread_mutex_lock(&mutex_list);
          show_name();
          pthread_mutex_unlock(&mutex_list);
          break;

        case 4:
          pthread_mutex_lock(&mutex_list);
          if(!is_book_empty()){
            printf("\nEnter the first name of the person you would like to delete: ");
            scanf("%s", del_fname);
            printf("\nEnter their last name: ");
            scanf("%s", del_lname);
            delete(del_fname, del_lname);
          }
          else{
            printf("\nThere are no entries in the phonebook to delete\n");
          }
          pthread_mutex_unlock(&mutex_list);
          break;

        case 5:
          pthread_mutex_lock(&mutex_list);
          if(!is_book_empty()){
            printf("\nEnter a name you would like to delete: ");
            scanf("%s", del_all);
            delete_name(del_all);
          }
          else{
            printf("\nThere are no entries in the phonebook to delete\n");
          }
          pthread_mutex_unlock(&mutex_list);
          break;

        case 6:
          pthread_mutex_lock(&mutex_bin);
          pthread_mutex_lock(&mutex_list);
          read_from_bin(binfile);
          pthread_mutex_unlock(&mutex_list);
          pthread_mutex_unlock(&mutex_bin);
          break;
          
        case 0:
          printf ("exit\n");
          exiting = 1;
          save_to_file(txtfile);
          return 0;
        
        default:
          printf("wrong option\n");
        }
    }
}
//autosave thread
void *autosave_thread(void * arg){
  char * binfile = (char*)arg;
  int o_state;
  
  while(exiting != 1){
    pthread_setcancelstate(PTHREAD_CANCEL_DISABLE, &o_state);
    pthread_mutex_lock(&mutex_bin);
    pthread_mutex_lock(&mutex_list);
    save_to_bin(binfile);
    pthread_mutex_unlock(&mutex_list);
    pthread_mutex_unlock(&mutex_bin);
    pthread_setcancelstate(o_state, &o_state);
    sleep(15);
  }
}





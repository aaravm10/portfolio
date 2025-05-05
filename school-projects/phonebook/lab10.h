
#ifndef LAB10_H
#define LAB10_H

//unions
typedef union
{
  int   bday[2];    // flag = 0
  char  ophone[20]; // flag = 1
} PERSON;

// structs
typedef struct book 
{
  char   f_name[20];
  char   l_name[20];
  char   phone_num[20];
  int    flag;
  PERSON person;
  struct book *next;
} BOOK; 

//variable declaration
extern BOOK *heads[];
extern unsigned char enckey;

// functions
int    main (int argc, char* argv[]);
void   read_from_keyboard(void);
void   insert(BOOK *temp);
void   show_all(void);
void   show_name(void);
void   delete(char [], char[]);
void   delete_name(char []);
int    check_duplicate(char [], char []);
void   read_from_file(char *file_name);
void   save_to_file(char *file_name);
void   delete_all(BOOK *head);
int    is_book_empty();
void   save_to_bin(char * filename);
void   save_headto_bin(FILE *bfp, BOOK *b);
void   read_from_bin(char *filename);
void   *main_thread(void * arg);
void   *autosave_thread(void * arg);
void   delete_heads(void);
#endif

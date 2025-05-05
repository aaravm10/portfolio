// includes
#include <stdio.h>
#include <string.h>
#include "lab10.h"
#include <stdlib.h>
#include <pthread.h>

// global variables
BOOK *heads[3];

//insert function
void read_from_keyboard(void){
  //local variable
  char f_added[20];
  char l_added[20];
  char phone_added[20];
  int type;
  int month;
  int day;
  BOOK *temp;
  BOOK *p;
  int true = 0;

  //taking and enterting input for name
  printf("\nPlease enter a first name: ");
  scanf("%s", f_added);
  printf("\nPlease enter a last name: ");
  scanf("%s", l_added);

  //checking if name already exists in array
  if(check_duplicate(f_added, l_added) == 1){
    return;
  }

  //taking and entering input for phone number
  printf("\nEnter the phone number for %s %s: ", f_added, l_added);
  scanf("%s", phone_added);

  //adding name if not already in array
  //sorting array
  temp = (BOOK*)malloc(sizeof(BOOK));
  strcpy(temp->f_name, f_added);
  strcpy(temp->l_name, l_added);
  strcpy(temp->phone_num, phone_added);

  while(true == 0){
    printf("\nAre you a close friend (0) , work colleague (1), or neither (2): ");
    scanf("%d",&type);

    if(type == 0){
      temp->flag = 0;
      int valid = 0;
      while(valid == 0){
        printf("\nEnter birthday");
        printf("\nMonth: ");
        scanf("%d", &month);
        printf("Day: ");
        scanf("%d", &day);
        if(month > 12 || day > 31){
          printf( "\nInvalid birthday\n");
        }
        else{
          temp->person.bday[0] = month;
          temp->person.bday[1] = day;
          valid = 1;
        }
      }
      true = 1;
    }
    else if(type == 1){
      temp->flag = 1;
      printf("\nEnter your office phone number: ");
      scanf("%s",temp->person.ophone);
      true = 1;
    }
    else if(type == 2){
      temp->flag = 2;
      true = 1;
    }
    else{
      printf("\nInvalid option\n");
    }
  }
  insert(temp);
}

int find_head(char* l_name){
  int x;
  if(l_name[0] <= 'k'){
    x=0;
  }
  else if(l_name[0]<'r'){
    x=1;
  }
  else{
    x=2;
  }
  return x;
}

void insert(BOOK *temp)
  {
  BOOK *p;
  BOOK *head;
  int head_idx = find_head(temp->l_name);

  head = heads[head_idx];

  if(head == NULL){
      head = temp;
      temp->next = NULL;
  }
  else{
    if(strcmp(head->l_name, temp->l_name) > 0){
      temp->next = head;
      head = temp;
    }
    else if (strcmp(head->l_name, temp->l_name) == 0 && strcmp(head->f_name, temp->f_name) > 0){
      temp->next = head;
      head = temp;
    }
    else{
      p = head;
      while(p->next != NULL){
        if(strcmp(p->next->l_name, temp->l_name) > 0){
          break;
        }
        else if(strcmp(p->next->l_name, temp->l_name) == 0){
          if(strcmp(p->next->f_name, temp->f_name) > 0){
            break;
          }
        }
        p = p->next;
      }
      if(p->next == NULL){
        temp->next = NULL;
        p->next = temp;
      }
      else{
        temp->next = p->next;
        p->next = temp;
      }
    }
  }
  heads[head_idx] = head;
}

//show all function
void show_all()
  {
    //local variables
    BOOK *p;
    int i;

    if(is_book_empty()){
      printf("No entries in phonebook\n");
      return;
    }
    
    for(i = 0; i < 3; i++){
      p = heads[i];

      //looping through array and printing values
      while(p != NULL){
        //returning all names and numbers
        printf("\nName: %s %s Phone:%s\n",p->f_name,p->l_name,p->phone_num);
        if(p->flag == 0){
          printf("Birthday: %d/%d\n",p->person.bday[0],p->person.bday[1]);
        }
        else if(p->flag == 1){
          printf("Office Phone: %s\n",p->person.ophone);
        }
        p = p->next;
      }
    }
  }

int is_book_empty(void){
  int i;
  for(i=0;i<3;i++){
    if(heads[i]!=NULL){
      return 0;
    }
  }
  return 1;
}

//show name function
void show_name(void)
  {
    //local variables
    char last[20];
    BOOK *p;
    int check = 0;
    int i;

    if(is_book_empty()){
      printf("No entries in phonebook\n");
      return;
    }

    //asking and getting user input
    printf("\nEnter a last name: ");
    scanf("%s", last);

    p = heads[find_head(last)];
    
    while(p != NULL){
      if(strcmp(p->l_name, last) == 0){
        check = 1;
        printf("Name: %s %s\n", p->f_name, last);
        printf("Phone number: %s \n",  p->phone_num);
        if(p->flag == 0){
          printf("Birthday: %d/%d\n",p->person.bday[0],p->person.bday[1]);
        }
        else if(p->flag == 1){
          printf("Office Phone: %s\n",p->person.ophone);
        }
      }
      p = p->next;
    }

    if(check == 0){
      printf("No last name \"%s\" was found\n", last);
    }
  }

//check duplicate function
int check_duplicate(char a[], char b[]){
  BOOK *comp;
  comp = heads[find_head(b)];

  while(comp != NULL){
    if(strcmp(comp->f_name, a) == 0 && strcmp(comp->l_name, b) == 0){
      printf("\nName has already been entered\n");
      return 1;
    }
    comp = comp->next;
  }
  return 0;
}

//delete function
void delete(char f[], char l[]){
  //declaring variables
  BOOK *p;
  BOOK * del;
  int check = 0;

  int head_idx = find_head(l);
  p = heads[head_idx];

  //checking if name is head 
  if(strcmp(p->f_name, f) == 0 && strcmp(p->l_name, l) == 0){
    del = p;
    p = p->next;
    heads[head_idx] = p;
    free(del);
    check = 1;
    return;
  }
  //checking if there is only 1 element
  if (p->next == NULL){
    if(strcmp(p->f_name, f) == 0 && strcmp(p->l_name, l) == 0){
      printf("only one element\n");
      free(p);
      check = 1;
      heads[head_idx] = NULL;
    }
  }
  //finding element in linked list
  else {
    while(p->next != NULL){
      if(strcmp(p->next->f_name, f) == 0 && strcmp(p->next->l_name, l) == 0){
        printf("found (more than 1 element)\n");
        del = p->next;
        p->next = del->next;
        free(del);
        check = 1;
        break;
      }
      p = p->next;
    }
  }
  //if name not found
  if(check == 0){
    printf("Name not found\n");
  }
}

//delete name function (deletes all names with same first name)
void delete_name(char f[]){
  //declaring variables
  BOOK *p;
  BOOK *del;
  BOOK *head;
  int check = 0;
  int i;

  for(i = 0; i<3; i++){
    head = heads[i];
    p = heads[i];
    //if list is empty
    if(head == NULL){
      continue;
    }
    //if element is head
    if(strcmp(head->f_name,f)==0){
      p = head->next;
      while(head!=NULL){
        if(strcmp(head->f_name,f)==0){
          free(head);
          head = p;
          if(p!= NULL){
            p = p->next;
          }
          check = 1;
        }
        else{
          break;
        }
      }
    }
    if(head != NULL){
      p = head;
      while(p->next != NULL){
        if(strcmp(p->next->f_name,f)==0){
          del = p->next;
          p->next = del->next;
          free(del);
          check = 1;
        }
        p = p->next;
        if(p == NULL){
          break;
        }
      }
    }
    heads[i] = head;
  }
  //no name found
  if(check == 0){
    printf("No Name found\n");
  }
}
  
//delete all function (free nodes)
void delete_all(BOOK *head){
  if(head == NULL){
    return;
  }
  delete_all(head->next);
  free(head);
}

void delete_heads(void){
  int i;
  for(i = 0; i<3; i++){
    delete_all(heads[i]);
  }
}
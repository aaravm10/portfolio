#include <stdio.h>
#include <string.h>
#include "lab10.h"
#include <stdlib.h>
#include <pthread.h>

void encrypt_string(char * d, char * s, unsigned char key){
  int i;

  for(i = 0; i<strlen(s); i++){
    d[i] = s[i]^key;
  }
}

void encrypt_write(FILE *fp, unsigned char key, BOOK *p){
  char s[128];
  char encrypt[128];
  int i;

  sprintf(s, "%s %s %s %d", p->f_name,p->l_name, p->phone_num, p->flag);
  encrypt_string(encrypt,s,key);
  fwrite(encrypt, strlen(s), 1, fp);
  if(p->flag == 0){
    sprintf(s, " %d/%d\n",p->person.bday[0], p->person.bday[1]);
    encrypt_string(encrypt,s,key);
    fwrite(encrypt, strlen(s), 1, fp);
  }
  else if(p->flag == 1){
    sprintf(s, "%s\n",p->person.ophone);
    encrypt_string(encrypt,s,key);
    fwrite(encrypt, strlen(s), 1, fp);
  }
  else{
    sprintf(s, "\n");
    encrypt_string(encrypt,s,key);
    fwrite(encrypt, strlen(s), 1, fp);
  }
}

void decrypt_string(char* s, unsigned char key, int len){
  int i;

  for(i = 0; i<len; i++){
    s[i] = s[i]^key;
  }
}


void read_from_file(char *file_name){
  FILE *fp;
  int filesize;
  
  fp = fopen(file_name, "r");

  BOOK *temp;
  char *filedata;
  char f_name[20];
  char l_name[20];
  char phone_num[20];
  int bday[2];
  char ophone[20];
  int flag;
  int count = 0;
  char * line;
  char  * sep = "\n";

  if(fp == NULL){
    return;
  }

  fseek(fp, 0L, SEEK_END);
  filesize = ftell(fp);
  fseek(fp, 0L, SEEK_SET);
  filedata = (char*)malloc(filesize);
  fread(filedata, filesize, 1, fp);
  
  decrypt_string(filedata, enckey, filesize);
  for(line = strtok(filedata, sep) ;
      line != NULL;
      line = strtok(NULL, sep)) {
      sscanf(line, "%s %s %s %d%n",f_name, l_name, phone_num, &flag, &count);
        line = line + count;
        temp = (BOOK*)malloc(sizeof(BOOK));
        strcpy(temp->f_name, f_name);
        strcpy(temp->l_name, l_name);
        strcpy(temp->phone_num, phone_num);
        temp->flag = flag;
        if(flag == 0){
          sscanf(line,"%d/%d", &bday[0],&bday[1]);
          temp->person.bday[0] = bday[0];
          temp->person.bday[1] = bday[1];
        }
        else if(flag == 1){
          sscanf(line, "%s", ophone);
          strcpy(temp->person.ophone, ophone);
        }
        insert(temp);
      }
  fclose(fp);
  return;
}


void save_head_tofile(FILE *fp, BOOK *b){
  BOOK *p;

  p = b;

  while(p!= NULL){
    encrypt_write(fp, enckey, p);
    p = p->next;
  }
}

void save_to_file(char* filename){
  FILE *fp;
  int i;
  fp = fopen(filename, "w");
  for(i = 0; i<3; i++){
    save_head_tofile(fp,heads[i]);
  }
  fclose(fp);
}


void save_to_bin(char * filename){
  FILE *bfp;
  int i;
  bfp = fopen(filename, "wb");
  for(i = 0; i<3; i++){
    save_headto_bin(bfp,heads[i]);
  }
  fclose(bfp);
}

void save_headto_bin(FILE *bfp, BOOK *b){
  BOOK *p;

  p = b;

  while(p!=NULL){
    fwrite(p, sizeof(BOOK), 1, bfp);
    p = p->next;
  }
}

void read_from_bin(char *filename){
  FILE *bfp;
  bfp = fopen(filename, "rb");
  BOOK p;

  if(bfp == NULL){
    return;
  }

  while(fread(&p,sizeof(BOOK), 1, bfp) == 1){
    printf("\nName: %s %s Phone:%s\n",p.f_name,p.l_name,p.phone_num);
    if(p.flag == 0){
      printf("Birthday: %d/%d\n",p.person.bday[0],p.person.bday[1]);
    }
    else if(p.flag == 1){
      printf("Office Phone: %s\n",p.person.ophone);
    }

  }
  fclose(bfp);
}
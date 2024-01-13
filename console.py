#!/usr/bin/python3
""" The entry point of the command interpreter"""

import cmd
import re
import json
from datetime import datetime
from models.base_model import BaseModel
from models import storage
from models.user import User


try:
    import gnureadline as readline
except ImportError:
    import readline

readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')


def normalize_value(str_v):
    """function to normalize values"""
    # check if the value is an integer
    if str_v.isdigit() or (str_v[0] == '-' and str_v[1:].isdigit()):
        return int(str_v)
    # if its just a regular string but has double quotes
    elif str_v.startswith('"') and not str_v.endswith('"'):
        return str_v.stri('"')

    # check if the value is a float
    try:
        return float(str_v)
    except (ValueError, Exception):
        # return as it is if neither int or float
        return str_v.strip('"')

    # check if the attr is enclosed in double quotes
    if str_v.startswith('"') and str_v.endswith('"'):
        return str_v[1:-1]  # Remove the double quotes
    else:
        return str_v.strip('"')  # remove the double uotes if found


class_list = {'BaseModel': BaseModel, 'User': User}


class HBNBCommand(cmd.Cmd):
    """ inheriting the Cmd class to customize it by ourself"""
    prompt = ('(hbnb) ')

    def do_quit(self, args):
        """ Quit command to exit the program"""
        return True

    def do_EOF(self, args):
        """ EOF command to exit the program"""
        return True

    def do_emptyline(self, line):
        """Do nothing on empty lines."""
        pass

    def do_create(self, args):
        """Create new instance of a class given in {args}"""
        if args:
            if args not in class_list:
                print("** class doesn't exist **")
                return
            args = args.split()
            new_inst = class_list[args[0]]()
            new_inst.save()
            print(new_inst.id)
        else:
            print("** class name missing **")

    def do_show(self, args):
        """Prints the string representation of an instance based on the class name and id"""
        if args:
            flag = 0
            words = args.split()
            if len(words) < 2:
                print("** instance id missing **")
                return
            if words[0] not in class_list:
                print("** class doesn't exist **")
                return
            else:
                all_obj = storage.all()
                instance_key = "{}.{}".format(words[0], words[1])

                for key, obj in all_obj.items():
                    if key.split('.')[1] == words[1]:
                        print(BaseModel.to_dict(obj))
                        flag = 1
                        break

                if flag == 0:
                    print("** no instance found **")

    def do_destroy(self, args):
        """Deletes an instance based on class name and id"""
        if args:
            flag = 0
            words = args.split()
            if len(words) < 2:
                print("** instance id missing **")
                return
            if words[0] not in class_list:
                print("** class doesn't exist **")
                return

            all_obj = storage.all()
            instance_key = "{}.{}".format(words[0], words[1])

            for key, obj in all_obj.items():
                if key.split('.')[1] == words[1]:
                    del all_obj[instance_key]
                    storage.save()
                    flag = 1
                    break

            if flag == 0:
                print("** no instance found **")

        else:
            print("** class name missing **")

    def do_all(self, args):
        """Prints all string representation of all instances"""
        words = args.split()
        class_name = None
        if words and words[0] not in class_list:
            print("** class doesn't exist **")
            return
        if words:
            class_name = words[0]
        instances = storage.all()
        instances_list = []
        for instance_key in instances:
            if class_name is None or instance_key.startswith(class_name):
                instances_list.append(str(instances[instance_key]))
        print(instances_list)

    def do_update(self, args):
        """Updates an instance on the class name and id"""
        args = args.split()
        if not args:
            print("** class name missing **")
            return
        if args[0] not in class_list:
            print("** class doesn't exist **")
            return

        if len(args) < 2:
            print("** instance id missing **")
            return

        all_obj = storage.all()
        instance_key = "{}.{}".format(args[0], args[1])

        if instance_key not in all_obj:
            print("** no instance found **")
            return

        if len(args) < 3:
            print("** attribute name missing **")
            return
        if len(args) < 4:
            print("** value missing **")
            return
        if args and args[0] not in class_list:
            print("** class doesn't exist **")
            return
        instance = all_obj[instance_key]
        if args[2].startswith('{') and args[-1].endswith('}'):
            try:
                # convert single quotes
                json_str = ' '.join(args[2:])
                value_dict = json.loads(json_str)

                for key, value in value_dict.items():
                    setattr(instance, key, value)
            except (json.JSONDecodeError, Exception) as e:
                print("json.JSONDecodeError ", str(e))
                pass

            attr_name = args[2].strip('"')
            value = ' '.join(args[3:]).strip('"')  # Join val wt spaces
            # set the new attr for the specific instance
            setattr(instance, attr_name, normalize_value(value))

        instance.updated_at = datetime.now()
        instance.save()


if __name__ == '__main__':
    HBNBCommand().cmdloop()

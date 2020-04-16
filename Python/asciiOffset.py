def offset(string="", n=0):
    new_string = ""
    for char in string:
        new_char_ord = ord(char)+n
        if new_char_ord > 126:
            new_char_ord = new_char_ord - 95
        if new_char_ord < 32:
            new_char_ord = new_char_ord + 95
        new_char = chr(new_char_ord)
        new_string = new_string+new_char
    print("from : "+string + " to : ")
    print(new_string)
    return new_string

#main offset
if __name__ == "__main__":
    userString = input("Type string to offset : ")
    while True:
        error = False
        userValue = input("Enter offset (integer needed) : ")
        if userValue in ["break", "quit", "abort"]:
            exit("User interrupted")

        try:
            userValue = int(userValue)
        except ValueError:
            error = True

        if not error:
            break
        else:
            print("type break to abort")
    result = offset(userString, userValue)
    print(result)

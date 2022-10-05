import schema_loader as sl

if __name__ == "__main__":
    if sl.update_schemas():
        print("success")
    else:
        print("fail")

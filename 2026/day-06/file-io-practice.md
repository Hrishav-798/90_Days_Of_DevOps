# Linux Fundamentals – Day 06

Today, I practiced basic file I/O operations in Linux, like creating a file, trying out different text editors, and viewing the contents.

## Creating a file
I started by creating a new empty text file using the `touch` command:
```bash
touch abc.txt
```

## Editing the file
First, I opened it with `nano` and added some text.
```bash
nano abc.txt
```

Then, I wanted to try out `vim`, but it turns out I don't have it installed yet!
```bash
$ vim abc.txt

Command 'vim' not found, but can be installed with:
sudo apt install vim        # version 2:9.1.0016-1ubuntu7.17, or
sudo apt install vim-gtk3   # version 2:9.1.0016-1ubuntu7.17
sudo apt install vim-motif  # version 2:9.1.0016-1ubuntu7.17
sudo apt install vim-nox    # version 2:9.1.0016-1ubuntu7.17
sudo apt install neovim     # version 0.7.2-8
```

Since `vim` wasn't there, I just went back to `nano` to finish my edits.
```bash
nano abc.txt
```

## Viewing the content
Finally, I used the `cat` command to print the contents of the file to the terminal to verify everything worked:
```bash
$ cat abc.txt
Hellooooo



Aspiring DevOps Engineer here
```

All good!

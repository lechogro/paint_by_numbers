##############################################
##### "Paint by Numbers" nonogram solver #####
##############################################

Created by Lechosław Grochowski (Poland), 2024-2025, contact: lechogro [you-know-what] gmail [dot] com
Currently available only as Python source code, also packed to Windows 32- and 64-bit EXE files with PyInstaller tool.
Online version is planned ;)
You are free to copy and reuse the program and the source code, but please include the information about the author.

1. Interface

The program very simple interface consists of the following objects:
*) "Load..." button - see "2. Loading nonograms".
*) "Reload" button - brings the program to the state just after loading the file, resetting any progress.
*) "Step >" button - performs one step of solving - see "3. Solving - standard".
*) "Solve >>" button - performs as many steps of solving as it is required to solve the picture. If no other steps are successful and the option "use also brute-force approach" is enabled, then the program automatically switches to the brute-force mode.
*) "Preview" checkbox - enables a preview in brute-force mode - see "5. Solving - brute-force". If selected, each created picture is shown, what decreases the speed of solving, sometimes really significantly.
*) "Use also brute-force approach" checkbox - enables brute-force approach (see "5. Solving - brute-force"). Otherwise, when standard approach does not succeed, the program remains the picture unsolved so that You can finish it ;)
*) Selecting solution spinbox - active only in brute-force mode, as standard mode does not support multiple solutions.
*) Clickable picture - toggles the state of the cells: unknown (gray) -> removed (white) -> filled (black). Both left and right mouse buttons can be used. Clicking reaction is inactive in the brute-force mode.

2. Loading nonograms

Nonogram descripting numbers are loaded from text files with following format:

rows
1,5
1 1
1,1,2
1,1,1
5 5

cols
5
1
1
1
1

0

5
1,1
1,1
1,1,1
1,3

After solving it gives:
# . . . . . # # # # #
# . . . . . # . . . .
# . . . . . # . . # #
# . . . . . # . . . #
# # # # # . # # # # #

Remarks:
*) Texts "rows" and "cols" can be replaced to anything else - the program checks only first sign in line, if it is a digit or not. However, you have to specify ROWS FIRST, then columns.
*) Acceptable separators are both commas and spaces - they are treated in the same way and can be mixed, as in the example above.
*) Empty text lines are ignored, so You can e.g. group every 5 lines. To put an empty row or column, use 0, as in the example above.

3. Solving - standard

The first stage of solving is trying to use the specific procedure on rows, columns, rows, columns etc., skipping completed ones. The procedure used on all rows is referred here as a step, then another step concerns all columns, then another step concerns all rows. If no progress is done in 2 subsequent steps for rows and columns, then:
*) If everything is done, the final check is performed.
*) If something is not done and the option "Use also brute-force approach" is enabled, the brute-force solving is started.
*) If something is not done and the option "Use also brute-force approach" is disabled, the program just stops. You can help it clicking on the picture and hence giving the program further information.

If You want to avoid arduous work, but have some fun, it is recommended not to use brute-force approach and stay only in the standard mode.

4. Solving - standard - details

The main concept of standard mode are blocks of non-removed cells, which contain blocks of filled cells. See the example below:
??###?...???##?##...#.?.
There are 4 non-removed blocks here:
*) ??###? - it contains one filled block: ###
*) ???##?## - it contains two filled blocks: ## and ##
*) # - it contains one filled block: #
*) ? - it does not contain any filled block.

After finding blocks, describing numbers are assigned to non-removed blocks and the result is kept in the assignment matrix. Assumptions:
*) Non-removed blocks have to be long enough. For example, if we have a row / column ..?????.??###??.????, then the describing number 5 may be in the 1st and 2nd non-describing block, but cannot be in the 3rd, since its length is only 4.
*) There cannot be too many describing numbers in the first and the last non-removed block. For example, if we have a row / column ..?????.???.????. and describing numbers 2 3 2, then it is impossible to fit both 2 and 3 to the first non-removed block, as well as both 3 and 2 to the last non-removed block. Hence the assignment matrix would be as follows:
         n o n
         r e m
         b l o
         1 2 3
   d n 2 + + -
   e u 3 - + -
   s m 2 - + +
*) The order of describing numbers has to be proper and refer to already known positions. For example, if we have a row / column ??????.???##???.??????, describing numbers 2 3 2 and we somehow know that the second describing number has to be in the second non-removed block, then the assignment matrix would be as follows:
         n o n
         r e m
         b l o
         1 2 3
   d n 2 + + -
   e u 3 - + -
   s m 2 - + +
The second row in the matrix bases on already had knowledge, while the first and the third consider that previous numbers cannot be in next blocks and next numbers cannot be in previous blocks.

Special cases considered by the algorithm:
*) If the number of filled cells in row / column is equal to the sum of all describing numbers, then the other cells have to be removed.
*) If the number of describing numbers in row / columns is equal to the number of non-removed blocks and each non-removed block contains exactly one filled block, then these filled blocks have to be described by different describing numbers (none of them can be connected) and all describing numbers have to be used.

After creating, the assignment matrix is summarized and the conclusions can be as follows:
*) If an assignment matrix column is empty, then it means, that nothing can be put in this non-removed block, so all cells there are marked as removed (as a result, this non-removed block disappears).
*) If an assignment matrix row is empty, then we gain a contradiction, as we expect that each describing number can be assigned somewhere. In the standard mode a message is shown and solving process is stopped as it is impossible to complete. In the brutal mode the program starts solving another variant.
*) If an assignment matrix row has exactly one element, then the describing number has to be in one particular non-removed block, hence this block is chosen to further reasoning.

As far as one non-removed block is concerned, first of all the extreme arrangements are tested and their intersection is created. For example, if we have describing numbers 3 1 2 and we are sure that they are all in non-removed block of length 10, then we have two extreme arrangements:
333 1 22  
  333 1 22
Hence their intersection is:
  3       

However, filled blocks in rows can come from columns and inversely, so not always their assignments to describing numbers are known. For each describing number that can be (note: not "must be", as it was in the case of the extreme arrangements) in this non-removed block, the following tests are performed and only these which pass all of them are considered:
*) The describing number has to be at least as big as the length of the filled block.
*) There has to be enough place before and after the filled block to fit blocks connected to other describing numbers (regardless of non-removed block partition). For example, if we have a row / column ???.?#?##????? and describing numbers 5 2, then the filled block # cannot be described with the number 2, as there are no 6 (5 + additional separator) non-removed cells before.

Further reasoning is similar to the situation with the describing number to non-removed block assignment matrix. If no number matches the filled block, then we get a contradiction. If only one number matches the filled block, then this number is assigned, considering bouncing from the borders. For example, if we have a row / column ??.??#???? and we know that only number 5 matches the filled block #, then we have the following assignment, based on the extreme arrangements: ??.??555??

Other cases considered by the algorithm:
*) Whole filled block is found. For example, if we have ?333????, then this block cannot be extended, so there must be: .333.???
*) The filled block cannot be extended, because there are no describing numbers bigger than its length. For example, if we have only describing numbers 1 and 2, there is no 3 or bigger, and we have a filled block of length 2, then this filled block has to be separated, regardless of the question which number 2 it is described with. 
*) If there are only 2 filled blocks, 2 describing numbers and these blocks cannot be connected because the total length would be too big, then each of them is described by the different describing number. For example, if we have describing numbers 2 1 and a non-removed block ???#?#???, then there must be ???2?1???, what obviously gives ..22.1...
*) If 2 filled blocks are described with 2 consecutive numbers, then the place between them which cannot be reached, is marked as removed. For example, if we have ???2????3??? and there is no describing number between 2 and 3, then there must be ???2?.??3??? Cases with the first or with the last describing number are treated similarly, so in the given example if there are no other describing numbers, we have ..?2?.??3??.

5. Solving - brute-force

Brute-force solving mode becomes active when the checkbox "Use also brute-force approach" is selected and if using only standard mode it is impossible to solve the picture. Its idea is creating the binary tree of all solutions and searching it depth-first, rejecting all contradictory cases. To reduce the number of steps, the way of creating new solutions is based on an empirically created Performance Index for each row and each column. It is given by the difference x-y, where x is the biggest describing number not referring to any completed non-removed block and y is the number of unknown cells. It can be considered as a degree of predictability of still unknown part in a row or a column: the bigger, the better. A row or a column with the biggest Performance Index is chosen to create two solutions: where first unknown cell in the selected row or column is either filled, or removed. Then standard solving takes place and after it new solution candidates are created recursively unless there was any contradiction or there are no empty cells to fill or remove.

The steps described here can be visualised with the "Preview" option, but it significantly decreases the speed of solving. However, even without it, the solving time can be sometimes very, very long. For example for 10x10 picture described by one "1" in each row and column, there are 10! = 3 628 800 possible solutions. To interrupt solving, deselect the "Use also brute-force approach" checkbox.

#####################
##### Have fun! #####
#####################

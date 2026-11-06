`timescale 1ns / 1ps

module full_adder_4bit_tb;

    reg  [3:0] a;
    reg  [3:0] b;
    reg        cin;
    wire [3:0] sum;
    wire       cout;

    // Golden check
    wire [4:0] expected;
    assign expected = a + b + cin;

    integer errors = 0;
    integer i, j, k;

    full_adder_4bit uut (
        .a   (a),
        .b   (b),
        .cin (cin),
        .sum (sum),
        .cout(cout)
    );

    initial begin
        $dumpfile("../dump/full_adder_4bit.vcd");
        $dumpvars(0, full_adder_4bit_tb);

        $display("==================================================");
        $display("🚀 Starting 4-bit Full Adder exhaustive testbench...");
        $display("==================================================");

        for (k = 0; k < 2; k = k + 1) begin
            for (i = 0; i < 16; i = i + 1) begin
                for (j = 0; j < 16; j = j + 1) begin
                    a = i[3:0];
                    b = j[3:0];
                    cin = k[0];
                    #5;
                    if ({cout, sum} !== expected) begin
                        $display("❌ Mismatch at a=%d, b=%d, cin=%b | Got: {cout=%b, sum=%d}, Expected: %d",
                                 a, b, cin, cout, sum, expected);
                        errors = errors + 1;
                    end
                end
            end
        end

        #10;
        $display("==================================================");
        if (errors == 0) begin
            $display("✅ All 512 test cases PASSED successfully!");
        end else begin
            $fatal(1, "Total errors: %0d", errors);
        end
        $display("==================================================");
        $finish;
    end

endmodule
